from helpers.db_utils import redshift_engine, stage_data, create_fact_table
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import logging
from metrics import rows_staged,fact_table_created

def load_master_data(df, table_name, engine):
    logging.info(f"Loading master data into {table_name}")
    stage_data(engine, df, table_name)
    rows_staged.set(len(df))
def load_transactional_data(df, engine):
    logging.info(f"Loading transactional data into FactPayroll")
    create_fact_table(engine, engine.metadata)
    fact_table_created.set(1)
    stage_data(engine, df, 'FactPayroll')
    rows_staged.set(len(df))

#############################################


engine = redshift_engine()
metadata = MetaData()

import pandas as pd

from helpers.db_utils import stage_data


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

    total_master_rows = len(dim_employee_df) + len(dim_agency_df) + len(dim_title_df)

    stage_data(engine, dim_employee_df, 'dim_employee')
    stage_data(engine, dim_agency_df, 'dim_agency')
    stage_data(engine, dim_title_df, 'dim_title')
    print(f"Master data successfully transformed and staged.")
    print(f" - dim_employee: {len(dim_employee_df)} rows")
    print(f" - dim_agency: {len(dim_agency_df)} rows")
    print(f" - dim_title: {len(dim_title_df)} rows")
    print(f"Total master data staged: {len(dim_employee_df) + len(dim_agency_df) + len(dim_title_df)} rows")


transform_master_data(master_files)

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

    total_transactional_rows = len(fact_payroll_df)

    stage_data(engine, dim_employee_df, 'dim_employee')
    stage_data(engine, dim_agency_df, 'dim_agency')
    stage_data(engine, dim_title_df, 'dim_title')
    stage_data(engine, fact_payroll_df, 'fact_payroll')

    print(f"Transactional data successfully transformed and staged.")
    print(f" - fact_payroll: {len(fact_payroll_df)} rows")
    print(f"Total transactional data staged: {len(fact_payroll_df)} rows")
    total_rows = total_master_rows + total_transactional_row
    print(f"All data successfully transformed and staged.")
    print(f" - Total master data: {total_master_rows} rows")
    print(f" - Total transactional data: {total_transactional_rows} rows")
    print(f"Total data staged: {total_rows} rows")


