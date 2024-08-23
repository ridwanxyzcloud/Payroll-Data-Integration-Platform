import pandas as pd
import logging
from helpers.metrics import data_quality_issues,rows_validated, rows_transformed,missing_values_detected
from helpers.alert_utils import send_urgent_email

def validate_and_clean_data(df, dim_col):
    logging.info(f"Validating and cleaning data")

    total_rows = len(df)
    rows_validated.set(total_rows)

    for col in dim_col:
        if col not in df.columns:
            df[col] = None

    # Check for missing values
    missing = df.isnull().sum()
    missing_values_detected.set(missing.sum())  # Set the total number of missing values detected

    missing_percentage = (missing / total_rows) * 100

    # Log changes
    changes_log = []

    # Handling based on missing value percentages
    for col, pct in missing_percentage.items():
        if pct <= 5:
            df.dropna(subset=[col], inplace=True)
            changes_log.append(f"Dropped rows with missing values in {col} as it was <= 5%")
        elif 5 < pct <= 10:
            if df[col].dtype == 'object':  # Replace with 'UNKNOWN' for strings
                df[col].fillna('UNKNOWN', inplace=True)
                changes_log.append(f"Replaced missing string values in {col} with 'UNKNOWN'")
            else:
                mean_value = df[col].mean()
                df[col].fillna(mean_value, inplace=True)
                changes_log.append(f"Replaced missing numeric values in {col} with mean: {mean_value}")
        else:
            logging.error(f"Missing values in {col} exceed 10%. Manual intervention required.")
            send_urgent_email(
                subject=f"Data Quality Issue Detected in {col}",
                body=f"High percentage of missing values in {col}: {pct}%. Immediate attention required.",
                to_email="data.engineer@example.com"
            )
            raise ValueError(f"High percentage of missing values in {col}: {pct}%")

    # Anomaly detection
    for col in df.select_dtypes(include=['number']).columns:
        # Replace negative values
        if (df[col] < 0).any():
            df.loc[df[col] < 0, col] = df[col].mean()
            changes_log.append(f"Replaced negative values in {col} with mean.")

        # Replace values greater than 2 * standard deviation
        upper_bound = df[col].mean() + 2 * df[col].std()
        if (df[col] > upper_bound).any():
            df.loc[df[col] > upper_bound, col] = df[col].mean()
            changes_log.append(f"Replaced outliers in {col} (>{2} * SD) with mean.")

    # Log all changes made to a table or a file
    logging.info("Data Cleaning Summary: " + "; ".join(changes_log))

    df.drop_duplicates(inplace=True)
    rows_transformed.set(len(df))  # Set the number of rows transformed

    return df


import pandas as pd
import logging
from helpers.metrics import rows_validated, missing_values_detected, rows_transformed, data_quality_issues

def validate_and_clean_master_data(df, master_columns):
    """
    Validates and cleans a master data DataFrame by ensuring only specified columns are retained,
    standardizing column formats, checking for duplicates, and logging changes.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing master data to be validated and cleaned.
    master_columns : list
        A list of columns that should be present in the DataFrame. Any extra columns will be removed.

    Returns:
    --------
    pd.DataFrame
        The cleaned DataFrame with standardized columns, duplicates removed, and missing values handled.

    Notes:
    ------
    - Only columns listed in `master_columns` are retained; any extra columns are dropped.
    - Specific columns (`EmployeeID`, `TitleCode`, `AgencyID`) are converted to numeric types,
      with non-numeric values coerced to NaN.
    - Name columns (`LastName`, `FirstName`) are standardized to title case.
    - Duplicates in key columns (`EmployeeID`, `TitleCode`, `AgencyID`) are identified and removed,
      with a log entry made for any duplicate values found.
    - The function logs all changes made during the cleaning process and updates relevant metrics,
      such as the number of rows validated, missing values detected, and rows transformed.
    """

    logging.info("Validating and cleaning master data")

    # Record total rows before cleaning
    total_rows = len(df)
    rows_validated.set(total_rows)  # Set the number of rows being validated

    # Ensure only columns in master_columns are present, drop any extra columns
    available_columns = [col for col in master_columns if col in df.columns]
    df = df[available_columns]

    # Initialize changes log
    changes_log = []

    # Validate and clean specific columns
    for col in df.columns:
        if col in ['EmployeeID', 'TitleCode', 'AgencyID']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            changes_log.append(f"Converted non-numeric values in {col} to NaN.")
        elif col in ['LastName', 'FirstName']:
            df[col] = df[col].str.title()  # Standardize to title case
            changes_log.append(f"Standardized {col} to title case.")

    # Check for duplicates in key columns
    key_columns = [col for col in ['EmployeeID', 'TitleCode', 'AgencyID'] if col in df.columns]
    for col in key_columns:
        if df[col].duplicated().any():
            duplicated_values = df[col][df[col].duplicated()].tolist()
            logging.error(f"Duplicate values found in {col}: {duplicated_values}")
            data_quality_issues.inc()
            df.drop_duplicates(subset=[col], keep='first', inplace=True)

    # Check for missing values
    missing = df.isnull().sum()
    missing_values_detected.set(missing.sum())  # Set the total number of missing values detected

    # Log all changes made to the master data
    logging.info("Master Data Cleaning Summary: " + "; ".join(changes_log))

    # Record the number of rows after cleaning
    rows_transformed.set(len(df))  # Set the number of rows transformed

    return df


def print_summary_report(df, initial_row_count, changes_log):
    # Calculate current row count
    current_row_count = len(df)

    # Calculate number of duplicates
    num_duplicates = initial_row_count - current_row_count

    # Calculate missing values
    missing_values = df.isnull().sum()
    total_missing_values = missing_values.sum()

    # Missing values by column
    missing_values_report = missing_values[missing_values > 0]

    # Count of cleaned data actions
    cleaned_actions = [action for action in changes_log if 'Replaced' in action or 'Standardized' in action]

    # Print summary report
    print("Summary Report:")
    print(f"Initial number of rows: {initial_row_count}")
    print(f"Number of rows after cleaning: {current_row_count}")
    print(f"Number of removed duplicates: {num_duplicates}")
    print(f"Total missing values detected: {total_missing_values}")

    if not missing_values_report.empty:
        print("\nMissing values by column:")
        print(missing_values_report)
    else:
        print("No missing values detected.")

    if cleaned_actions:
        print("\nData Cleaning Actions:")
        for action in cleaned_actions:
            print(f" - {action}")
    else:
        print("No specific cleaning actions were performed.")


def harmonize_columns(df):
    """
    Harmonizes column names in the DataFrame by mapping variations of column names to a consistent naming convention.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame whose columns need to be harmonized.

    Returns:
    --------
    pd.DataFrame
        The DataFrame with harmonized column names.

    Notes:
    ------
    - The function currently harmonizes 'AgencyCode' to 'AgencyID'.
    - Additional column mappings can be added to the `column_mapping` dictionary as needed.
    """

    # Map variations to a consistent column name
    column_mapping = {
        'AgencyCode': 'AgencyID',  # Harmonize AgencyCode to AgencyID
    }

    # Rename columns according to the mapping
    df.rename(columns=column_mapping, inplace=True)

    return df


def validate_and_clean_transactional_data(df, transaction_columns):
    """
    Validates and cleans transactional data by performing several operations including harmonization of column names,
    handling missing values, detecting and handling anomalies, and standardizing specific columns.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing transactional data to be validated and cleaned.

    transaction_columns : list of str
        The list of columns that are required in the transactional data. The function will ensure these columns are present
        and will drop any other columns not in this list.

    Returns:
    --------
    pd.DataFrame
        The cleaned DataFrame with harmonized columns, handled missing values, and standardized formats.

    Process:
    --------
    - Harmonizes column names using `harmonize_columns`.
    - Validates the presence of required columns and removes any extra columns.
    - Checks for and handles missing values according to specific thresholds:
        - Drops rows where a column has <= 5% missing values.
        - Replaces missing string values with 'UNKNOWN' and numeric values with their mean where missing percentage is > 5% but <= 10%.
        - Raises an error and sends an urgent email if missing values exceed 10% in any column.
    - Handles anomalies:
        - Converts non-numeric values to NaN for key columns like EmployeeID, TitleCode, AgencyID, and PayrollNumber.
        - Replaces negative values with positive equivalents and outliers with the mean in measure columns.
        - Replaces outliers in 'FiscalYear' with the most frequent year.
    - Standardizes certain columns:
        - Converts names in 'FirstName' and 'LastName' to title case.
        - Converts categorical values like 'PayBasis' and 'WorkLocationBorough' to uppercase.
        - Converts 'AgencyStartDate' to datetime format.
    - Removes duplicate rows based on all columns.

    Metrics:
    --------
    - Updates several metrics like `rows_validated`, `missing_values_detected`, and `rows_transformed` during the process.
    - Logs all changes made to the data for traceability.

    Raises:
    -------
    ValueError
        If the missing values in any column exceed 10%, requiring manual intervention.

    Example Usage:
    --------------
    cleaned_df = validate_and_clean_transactional_data(df, transaction_columns)
    """

    logging.info("Validating and cleaning transactional data")

    df = harmonize_columns(df)

    total_rows = len(df)
    rows_validated.set(total_rows)  # Set the number of rows being validated

    # Ensure all required columns are present and drop any extra columns
    df = df[transaction_columns]

    # Check for missing values
    missing = df.isnull().sum()
    missing_values_detected.set(missing.sum())  # Set the total number of missing values detected

    missing_percentage = (missing / total_rows) * 100

    changes_log = []
    rows_before_cleaning = len(df)

    # Handling missing values based on percentage
    for col, pct in missing_percentage.items():
        if pct <= 5:
            df.dropna(subset=[col], inplace=True)
            changes_log.append(f"Dropped rows with missing values in {col} as it was <= 5%")
        elif 5 < pct <= 10:
            if df[col].dtype == 'object':
                df[col].fillna('UNKNOWN', inplace=True)
                changes_log.append(f"Replaced missing string values in {col} with 'UNKNOWN'")
            else:
                mean_value = df[col].mean()
                df[col].fillna(mean_value, inplace=True)
                changes_log.append(f"Replaced missing numeric values in {col} with mean: {mean_value}")
        else:
            logging.error(f"Missing values in {col} exceed 10%. Manual intervention required.")
            send_urgent_email(
                subject=f"Data Quality Issue Detected in {col}",
                body=f"High percentage of missing values in {col}: {pct}%. Immediate attention required.",
                to_email="data.engineer@example.com"
            )
            data_quality_issues.inc()
            raise ValueError(f"High percentage of missing values in {col}: {pct}%")

    # Handle anomalies for key columns separately
    key_columns = ['EmployeeID', 'TitleCode', 'AgencyID', 'PayrollNumber']
    for col in key_columns:
        if col in df.columns:
            # Convert non-numeric values to NaN for key columns
            df[col] = pd.to_numeric(df[col], errors='coerce')
            changes_log.append(f"Converted non-numeric values in {col} to NaN.")
            # Fill missing values with NaN for key columns
            df[col].fillna(pd.NA, inplace=True)

    # Handle anomalies for measure columns
    measure_columns = ['BaseSalary', 'RegularHours', 'RegularGrossPaid', 'OTHours', 'TotalOTPaid', 'TotalOtherPay']
    for col in measure_columns:
        if col in df.columns:
            # Replace negative values with their positive equivalents
            if (df[col] < 0).any():
                df.loc[df[col] < 0, col] = df[col].abs()
                changes_log.append(f"Replaced negative values in {col} with their positive equivalents.")

            # Handle outliers in measure columns
            mean_value = df[col].mean()
            std_dev = df[col].std()
            upper_bound = mean_value + 2 * std_dev
            lower_bound = mean_value - 2 * std_dev

            outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
            if outliers.any():
                df.loc[outliers, col] = mean_value  # Replace outliers with mean
                changes_log.append(f"Replaced outliers in {col} with mean value: {mean_value}")

    # Handle outliers in 'FiscalYear' column
    if 'FiscalYear' in df.columns:
        df['FiscalYear'] = pd.to_numeric(df['FiscalYear'], errors='coerce')
        mean_value = df['FiscalYear'].mean()
        std_dev = df['FiscalYear'].std()
        upper_bound = mean_value + 2 * std_dev
        lower_bound = mean_value - 2 * std_dev

        outliers = (df['FiscalYear'] < lower_bound) | (df['FiscalYear'] > upper_bound)
        if outliers.any():
            most_frequent_year = df['FiscalYear'].mode()[0]  # Get the most frequent year
            df.loc[outliers, 'FiscalYear'] = most_frequent_year
            changes_log.append(f"Replaced outlier FiscalYear values with most frequent year: {most_frequent_year}")

    # Standardize name columns
    if 'FirstName' in df.columns:
        df['FirstName'] = df['FirstName'].str.title()
        changes_log.append("Standardized FirstName to title case.")

    if 'LastName' in df.columns:
        df['LastName'] = df['LastName'].str.title()
        changes_log.append("Standardized LastName to title case.")

    # Standardize categorical columns
    categorical_columns = ['PayBasis', 'WorkLocationBorough']
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].str.upper()
            changes_log.append(f"Standardized {col} to uppercase.")

    # Standardize date columns
    if 'AgencyStartDate' in df.columns:
        df['AgencyStartDate'] = pd.to_datetime(df['AgencyStartDate'], errors='coerce')
        changes_log.append("Standardized AgencyStartDate to datetime format.")

    # Remove duplicate rows based on all columns
    df.drop_duplicates(inplace=True)

    logging.info("Transactional Data Cleaning Summary: " + "; ".join(changes_log))

    rows_transformed.set(len(df))  # Set the number of rows transformed

    return df

def second_dbt_validation(df, required_columns):
    logging.info("Validating and cleaning master data")

    total_rows = len(df)
    rows_validated.set(total_rows)  # Set the number of rows being validated

    # Ensure all required columns are present, even if they are empty
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
            logging.warning(f"Column {col} missing in the data. Added empty column.")
            data_quality_issues.inc()

    # Initialize changes log
    changes_log = []

    # Check and validate data types
    for col in df.columns:
        if col in ['EmployeeID', 'TitleCode', 'AgencyID']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            changes_log.append(f"Converted non-numeric values in {col} to NaN.")

    # Check for duplicates in key columns
    for col in ['EmployeeID', 'TitleCode', 'AgencyID']:
        if col in df.columns and df[col].duplicated().any():
            duplicated_values = df[col][df[col].duplicated()].tolist()
            logging.error(f"Duplicate values found in {col}: {duplicated_values}")
            data_quality_issues.inc()
            df.drop_duplicates(subset=[col], keep='first', inplace=True)

    # Cross-field validation
    if 'LeaveStatusasofJune30' in df.columns and 'EmployeeID' in df.columns and 'FirstName' in df.columns:
        inconsistent_rows = df[(df['LeaveStatusasofJune30'] == 'Active') & (df[['EmployeeID', 'FirstName']].isnull().any(axis=1))]
        if not inconsistent_rows.empty:
            logging.error(f"Inconsistent data detected in active employee records: {inconsistent_rows}")
            data_quality_issues.inc()

    # Validation of date ranges
    if 'AgencyStartDate' in df.columns:
        future_dates = df[df['AgencyStartDate'] > pd.Timestamp.today()]
        if not future_dates.empty:
            logging.error(f"Future dates found in AgencyStartDate: {future_dates}")
            df.loc[df['AgencyStartDate'] > pd.Timestamp.today(), 'AgencyStartDate'] = pd.NA
            changes_log.append("Replaced future dates in AgencyStartDate with NaN")

    # Standardize data formats
    if 'LastName' in df.columns:
        df['LastName'] = df['LastName'].str.title()
        changes_log.append("Standardized LastName to title case.")

    if 'LeaveStatusasofJune30' in df.columns:
        df['LeaveStatusasofJune30'] = df['LeaveStatusasofJune30'].str.upper()
        changes_log.append("Standardized LeaveStatusasofJune30 to uppercase.")

    # Ensure no rows are dropped, only duplicates are removed
    df.drop_duplicates(inplace=True)

    # Replace missing values
    missing = df.isnull().sum()
    missing_values_detected.set(missing.sum())  # Set the total number of missing values detected

    for col in df.columns:
        if df[col].dtype == 'object':  # For text-based columns
            if df[col].isnull().any():
                df[col].fillna('UNKNOWN', inplace=True)
                changes_log.append(f"Replaced missing string values in {col} with 'UNKNOWN'")
        elif df[col].dtype in ['int64', 'float64']:  # For numeric columns
            if df[col].isnull().any():
                df[col].fillna(pd.NA, inplace=True)
                changes_log.append(f"Replaced missing numeric values in {col} with NaN")
        elif pd.api.types.is_datetime64_any_dtype(df[col]):  # For date columns
            if df[col].isnull().any():
                df[col].fillna(pd.NA, inplace=True)
                changes_log.append(f"Replaced missing date values in {col} with NaN")

    # Log all changes made to the master data
    logging.info("Master Data Cleaning Summary: " + "; ".join(changes_log))

    rows_transformed.set(len(df))  # Set the number of rows transformed

    return df


