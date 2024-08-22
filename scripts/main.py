import pandas as pd
import logging
import boto3
import os
from io import StringIO
from helpers.db_utils import redshift_engine

# AWS and S3 configuration
s3_bucket = os.getenv("s3_bucket")
s3_prefix = os.getenv("s3_prefix")
aws_region = os.getenv("aws_region")
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")

# Database configuration
db_connection_string = os.getenv("db_connection_string")
engine = redshift_engine()

# Define schemas for dimension and fact tables
table_schemas = {
    'dim_employee': ['EmployeeID', 'FirstName', 'LastName'],
    'dim_agency': ['AgencyID', 'AgencyName', 'AgencyStartDate'],
    'dim_title': ['TitleCode', 'TitleDescription'],
    'fact_payroll': ['PayrollID', 'EmployeeID', 'FiscalYear', 'PayrollNumber', 'BaseSalary', 'RegularHours',
                     'RegularGrossPaid', 'OTHours', 'TotalOTPaid', 'TotalOtherPay', 'WorkBorough']
}


def initialize_s3_client(aws_region, aws_access_key_id, aws_secret_access_key):
    return boto3.client(
        's3',
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )


s3_client = initialize_s3_client(aws_region, aws_access_key_id, aws_secret_access_key)


def extract_from_s3(s3_client, s3_bucket, s3_prefix, file_name):
    try:
        logging.info(f"Extracting {file_name} from S3")
        obj = s3_client.get_object(Bucket=s3_bucket, Key=s3_prefix + file_name)
        df = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))
        return df
    except Exception as e:
        logging.error(f"Failed to extract {file_name}: {str(e)}")
        raise


def harmonize_columns(df):
    # Map variations to a consistent column name
    column_mapping = {
        'AgencyCode': 'AgencyID',  # Harmonize AgencyCode to AgencyID
    }
    # Rename columns according to the mapping
    df.rename(columns=column_mapping, inplace=True)
    return df


def validate_and_clean_master_data(df, master_columns):
    # Ensure all required columns are present
    df = df[master_columns]
    # Handle missing values
    df.dropna(subset=master_columns, inplace=True)
    return df


def validate_and_clean_transactional_data(df, transaction_columns):
    logging.info("Validating and cleaning transactional data")

    df = harmonize_columns(df)
    # Ensure all required columns are present
    df = df[transaction_columns]

    # Handle missing values
    for col in transaction_columns:
        if df[col].isnull().sum() > 0:
            if col in ['EmployeeID', 'TitleCode', 'AgencyID', 'PayrollNumber']:
                df[col].fillna('UNKNOWN', inplace=True)
            else:
                df[col].fillna(df[col].mean(), inplace=True)

    return df


def ensure_columns(df, columns):
    """Ensure the DataFrame has all the required columns, filling missing ones with NaN."""
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA
    return df[columns]


def transform_master_data(master_files):
    # Initialize empty DataFrames with the required columns
    dim_employee_df = pd.DataFrame(columns=table_schemas['dim_employee'])
    dim_agency_df = pd.DataFrame(columns=table_schemas['dim_agency'])
    dim_title_df = pd.DataFrame(columns=table_schemas['dim_title'])

    # Define a mapping from file names to dimension table names and their schemas
    file_to_table_map = {
        'EmpMaster.csv': ('dim_employee', table_schemas['dim_employee']),
        'AgencyMaster.csv': ('dim_agency', table_schemas['dim_agency']),
        'TitleMaster.csv': ('dim_title', table_schemas['dim_title'])
    }

    for file_name in master_files:
        table_name, required_columns = file_to_table_map.get(file_name)

        if table_name:
            # Extract data from the file
            df = extract_data(file_name)

            # Validate and clean the master data
            df_cleaned = validate_and_clean_master_data(df, required_columns)

            # Ensure the DataFrame has all required columns
            df_cleaned = ensure_columns(df_cleaned, required_columns)

            # Append data to the appropriate dimension DataFrame
            if table_name == 'dim_employee':
                dim_employee_df = pd.concat([
                    dim_employee_df,
                    df_cleaned.drop_duplicates()
                ], ignore_index=True)

            elif table_name == 'dim_agency':
                dim_agency_df = pd.concat([
                    dim_agency_df,
                    df_cleaned.drop_duplicates()
                ], ignore_index=True)

            elif table_name == 'dim_title':
                dim_title_df = pd.concat([
                    dim_title_df,
                    df_cleaned.drop_duplicates()
                ], ignore_index=True)

    return dim_employee_df, dim_agency_df, dim_title_df


def transform_transactional_data(payroll_files):
    # Initialize empty DataFrames for dimensions
    dim_employee_df = pd.DataFrame(columns=table_schemas['dim_employee'])
    dim_agency_df = pd.DataFrame(columns=table_schemas['dim_agency'])
    dim_title_df = pd.DataFrame(columns=table_schemas['dim_title'])

    fact_payroll_df = pd.DataFrame(columns=table_schemas['fact_payroll'])

    for file_name in payroll_files:
        # Extract data from the transactional files
        df = extract_from_s3(s3_client, s3_bucket, s3_prefix, file_name)

        # Clean and validate the transactional data
        df_cleaned = validate_and_clean_transactional_data(df, transaction_columns)

        # Update dimension DataFrames
        # For dim_employee
        dim_employee_data = df_cleaned[['EmployeeID', 'FirstName', 'LastName', 'LeaveStatusasofJune30']]
        dim_employee_df = pd.concat([
            dim_employee_df,
            ensure_columns(dim_employee_data, table_schemas['dim_employee']).drop_duplicates()
        ], ignore_index=True)

        # For dim_agency
        dim_agency_data = df_cleaned[['AgencyID', 'AgencyName', 'AgencyStartDate']]
        dim_agency_df = pd.concat([
            dim_agency_df,
            ensure_columns(dim_agency_data, table_schemas['dim_agency']).drop_duplicates()
        ], ignore_index=True)

        # For dim_title
        dim_title_data = df_cleaned[['TitleCode', 'TitleDescription']]
        dim_title_df = pd.concat([
            dim_title_df,
            ensure_columns(dim_title_data, table_schemas['dim_title']).drop_duplicates()
        ], ignore_index=True)

        # Prepare fact_payroll DataFrame
        df_cleaned['PayrollID'] = range(1, len(df_cleaned) + 1)
        fact_payroll_data = df_cleaned[['PayrollID', 'EmployeeID', 'FiscalYear', 'PayrollNumber', 'BaseSalary',
                                        'RegularHours', 'RegularGrossPaid', 'OTHours', 'TotalOTPaid', 'TotalOtherPay',
                                        'WorkLocationBorough']]
        fact_payroll_df = pd.concat([
            fact_payroll_df,
            ensure_columns(fact_payroll_data, table_schemas['fact_payroll']).drop_duplicates()
        ], ignore_index=True)

    # Return the dimension DataFrames and fact DataFrame
    return dim_employee_df, dim_agency_df, dim_title_df, fact_payroll_df


def load_data_to_edw(dim_employee_df, dim_agency_df, dim_title_df, fact_payroll_df):

    # Load dimension tables if they contain data
    if not dim_employee_df.empty:
        dim_employee_df.to_sql('dim_employee', engine, if_exists='replace', index=False)
    if not dim_agency_df.empty:
        dim_agency_df.to_sql('dim_agency', engine, if_exists='replace', index=False)
    if not dim_title_df.empty:
        dim_title_df.to_sql('dim_title', engine, if_exists='replace', index=False)

    # Load fact table if it contains data
    if not fact_payroll_df.empty:
        fact_payroll_df.to_sql('fact_payroll', engine, if_exists='replace', index=False)

    engine.close()


# Define master files and their respective schema names
master_files = ['EmpMaster.csv', 'TitleMaster.csv', 'AgencyMaster.csv']
payroll_files = ['nycpayroll_2020.csv', 'nycpayroll_2021.csv']
dim_table_names = ['dim_employee', 'dim_title', 'dim_agency']
dim_columns = [
    ['EmployeeID', 'LastName', 'FirstName', 'LeaveStatusasofJune30'],
    ['TitleCode', 'TitleDescription'],
    ['AgencyID', 'AgencyName', 'AgencyStartDate']
]

transaction_columns = [
    'FiscalYear', 'PayrollNumber', 'AgencyID', 'AgencyName', 'EmployeeID', 'LastName', 'FirstName',
    'AgencyStartDate', 'WorkLocationBorough', 'TitleCode', 'TitleDescription', 'LeaveStatusasofJune30',
    'BaseSalary', 'PayBasis', 'RegularHours', 'RegularGrossPaid', 'OTHours', 'TotalOTPaid', 'TotalOtherPay'
]


def main():
    # Ingest and transform data
    dim_employee_df, dim_agency_df, dim_title_df = transform_master_data(master_files)
    fact_payroll_df = transform_transactional_data(payroll_files)

    # Load data to EDW
    load_data_to_edw(dim_employee_df, dim_agency_df, dim_title_df, fact_payroll_df)


if __name__ == "__main__":
    main()
