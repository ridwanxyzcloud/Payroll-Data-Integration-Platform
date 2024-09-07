import pandas as pd
import logging
from scripts.extract import extract_data
from scripts.validate import validate_and_clean_master_data, validate_and_clean_transactional_data
from helpers.db_utils import stage_data
from helpers.metrics_server import (total_master_rows_extracted, master_files_count, total_rows_ingested, total_master_rows_ingested, total_transactional_rows_ingested, total_transactional_rows_extracted,transactional_files_count)

def ensure_columns(df, columns):
    """
    Ensure the DataFrame has all the required columns, filling missing ones with NaN.
    
    Args:
        df (pd.DataFrame): The DataFrame to check and modify.
        columns (list of str): The list of required column names.
        
    Returns:
        pd.DataFrame: The DataFrame with all required columns, filled with NaN where necessary.
    """
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA
    return df[columns]



def transform_master_data(master_files, table_schemas, s3_client, s3_bucket, s3_prefix, engine):
    """
    Transform and stage master data from given files into dimension tables.
    
    Args:
        master_files (list of str): List of file names containing master data.
        
    Returns:
        None
    """
    # Initialize empty DataFrames with the required columns based on table schemas
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
        table_name, required_columns = file_to_table_map.get(file_name, (None, None))

        if table_name:
            try:
                # Extract data from the file
                df = extract_data(file_name, s3_client, s3_bucket, s3_prefix)

                total_master_rows_extracted.inc(len(df))
                master_files_count.inc()
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
            
            except Exception as e:
                logging.error(f"Error processing file {file_name}: {e}")
                continue

    # Stage the data into the database
    try:
        stage_data(engine, dim_employee_df, 'dim_employee')
        stage_data(engine, dim_agency_df, 'dim_agency')
        stage_data(engine, dim_title_df, 'dim_title')
    except Exception as e:
        logging.error(f"Error staging data: {e}")
        return

    total_master_rows_staged = len(dim_employee_df) + len(dim_agency_df) + len(dim_title_df)

    # Update metrics for master data
    total_master_rows_ingested.inc(total_master_rows_staged)

    # Log success message with details
    logging.info("Master data successfully transformed and staged.")
    logging.info(f" - dim_employee: {len(dim_employee_df)} rows")
    logging.info(f" - dim_agency: {len(dim_agency_df)} rows")
    logging.info(f" - dim_title: {len(dim_title_df)} rows")
    logging.info(f"Total master data staged: {total_master_rows_ingested} rows")



def transform_transactional_data(payroll_files, table_schemas, attributes, s3_client, s3_bucket, s3_prefix, engine):
    """
    Transform and stage transactional data from the given payroll files into dimension and fact tables.

    Args:
        payroll_files (list of str): List of payroll file names to process.

    Returns:
        None
    """
    # 
    
    # Initialize empty DataFrames with the required columns based on table schemas
    dim_employee_df = pd.DataFrame(columns=table_schemas['dim_employee'])
    dim_agency_df = pd.DataFrame(columns=table_schemas['dim_agency'])
    dim_title_df = pd.DataFrame(columns=table_schemas['dim_title'])
    fact_payroll_df = pd.DataFrame(columns=table_schemas['fact_payroll'])

    for file_name in payroll_files:
        try:
            # Extract data from the transactional files
            df = extract_data(file_name, s3_client, s3_bucket, s3_prefix)

            total_transactional_rows_extracted.inc(len(df))
            transactional_files_count.inc()
        
            # Clean and validate the transactional data
            df_cleaned = validate_and_clean_transactional_data(df, attributes)

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
            fact_payroll_data = df_cleaned[['PayrollNumber', 'EmployeeID', 'AgencyID', 'TitleCode','FiscalYear', 'BaseSalary',
                                            'RegularHours', 'RegularGrossPaid', 'OTHours', 'TotalOTPaid', 'TotalOtherPay',
                                            'WorkLocationBorough']]
            fact_payroll_df = pd.concat([
                fact_payroll_df,
                ensure_columns(fact_payroll_data, table_schemas['fact_payroll']).drop_duplicates()
            ], ignore_index=True)
        
        except Exception as e:
            logging.error(f"Error processing file {file_name}: {e}")
            continue

    # Stage the data into the database
    try:
        stage_data(engine, dim_employee_df, 'dim_employee')
        stage_data(engine, dim_agency_df, 'dim_agency')
        stage_data(engine, dim_title_df, 'dim_title')
        stage_data(engine, fact_payroll_df, 'fact_payroll')
    except Exception as e:
        logging.error(f"Error staging data: {e}")
        return

    # Calculate total rows staged
    total_transactional_rows_staged = len(fact_payroll_df)
    #total_rows_staged = total_master_rows_staged + total_transactional_rows_staged

    # Update Prometheus metrics
    total_transactional_rows_ingested.set(total_transactional_rows_staged)
    
    #total_rows_ingested.set(total_rows_staged)
    
    # Log success message with details
    logging.info("Transactional data successfully transformed and staged.")
    logging.info(f" - fact_payroll: {total_transactional_rows_staged} rows")
    logging.info(f"Total transactional data staged: {total_transactional_rows_staged} rows")
    logging.info("All data successfully transformed and staged.")
    #logging.info(f"Total data staged: {total_rows_staged} rows")