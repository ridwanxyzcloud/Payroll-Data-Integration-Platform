import pandas as pd
import logging
from metrics import rows_processed, rows_cleaned, data_quality_issues


def validate_and_clean_data(df, dim_col):
    logging.info(f"Validating and cleaning data")

    # Update metric for rows processed
    rows_processed.set(len(df))

    for col in dim_col:
        if col not in df.columns:
            df[col] = None

    # Check for missing values
    missing = df.isnull().sum()
    total_rows = len(df)
    missing_percentage = (missing / total_rows) * 100

    # Log changes
    changes_log = []
    rows_before_cleaning = len(df)

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
            data_quality_issues.inc()  # Increment issue count
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

    # Update metric for rows cleaned
    rows_cleaned.set(len(df))

    return df
