import pandas as pd
import logging
from helpers.db_utils import read_table
from helpers.alert_utils import send_urgent_email
from helpers.metrics import rows_transformed, rows_validated, missing_values_detected

def validate_and_clean_data(df, dim_col):
    logging.info(f"Validating and cleaning data")

    total_rows = len(df)
    rows_validated.set(total_rows)  # Set the number of rows being validated

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

def transform_master_data(df, required_columns):
    return validate_and_clean_data(df, required_columns)

def transform_transactional_data(df, engine):
    df = validate_and_clean_data(df, ['EmployeeID', 'AgencyID', 'TitleCode'])

    dim_employee = read_table(engine, 'DimEmployee')
    df = pd.merge(df, dim_employee[['EmployeeID']], on='EmployeeID', how='left')

    dim_agency = read_table(engine, 'DimAgency')
    df = pd.merge(df, dim_agency[['AgencyID']], on='AgencyID', how='left')

    dim_title = read_table(engine, 'DimTitle')
    df = pd.merge(df, dim_title[['TitleCode']], on='TitleCode', how='left')

    return df
