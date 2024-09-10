import sys
import os

# PYTHONPATH for project directories
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import pandas as pd
import logging
from dotenv import load_dotenv

# Import your existing functions and utilities
from helpers.logging_utils import setup_logging
from helpers.db_utils import stage_data, redshift_engine
from scripts.transform_ingest import ensure_columns, transform_master_data, transform_transactional_data
from scripts.extract import extract_data
from scripts.validate import validate_and_clean_master_data, validate_and_clean_transactional_data
from helpers.s3_utils import get_s3_client
from helpers.metrics_server import (
    start_metrics_server, master_files_count, transactional_files_count,total_files_count,
    total_master_rows_extracted, total_transactional_rows_extracted, total_rows_extracted,
    total_master_rows_validated, total_master_rows_cleaned, missing_master_values_detected,
    total_transactional_rows_validated, total_transactional_rows_cleaned,missing_transactional_values_detected,
    data_quality_issues_master, data_quality_issues_transactional, total_rows_transformed,
    total_master_rows_ingested,total_transactional_rows_ingested,total_rows_ingested,
    total_master_rows_loaded,total_transactional_rows_loaded,total_rows_loaded)
from scripts.dbt_run import dbt_trigger



def load_env_and_setup():
    """
    Load environment variables and setup necessary configurations.
    """
    load_dotenv(override=True)

    setup_logging()

    start_metrics_server(port=8001)

    global s3_client, engine, s3_bucket, s3_prefix, table_schemas, attributes, master_files, payroll_files

    s3_client = get_s3_client()
    engine = redshift_engine()
    
    s3_bucket = os.getenv("s3_bucket")
    s3_prefix = os.getenv("s3_prefix")

    # Validate environment variables
    if not s3_bucket or not s3_prefix:
        logging.error("S3_BUCKET or S3_PREFIX environment variables are not set.")
        raise ValueError("S3_BUCKET or S3_PREFIX environment variables are not set.")

    table_schemas = {
        'dim_employee': ['EmployeeID', 'FirstName', 'LastName', 'LeaveStatusasofJune30'],
        'dim_agency': ['AgencyID', 'AgencyName', 'AgencyStartDate'],
        'dim_title': ['TitleCode', 'TitleDescription'],
        'fact_payroll': ['PayrollNumber', 'EmployeeID', 'AgencyID', 'TitleCode', 'FiscalYear', 'BaseSalary', 
                         'RegularHours', 'RegularGrossPaid', 'OTHours', 'TotalOTPaid', 'TotalOtherPay', 
                         'WorkLocationBorough']
    }

    attributes = [
        'FiscalYear', 'PayrollNumber', 'AgencyID', 'AgencyName', 'EmployeeID', 'LastName', 'FirstName',
        'AgencyStartDate', 'WorkLocationBorough', 'TitleCode', 'TitleDescription', 'LeaveStatusasofJune30',
        'BaseSalary', 'PayBasis', 'RegularHours', 'RegularGrossPaid', 'OTHours', 'TotalOTPaid', 'TotalOtherPay'
    ]

    # Define master and payroll files to be processed
    master_files = ['EmpMaster.csv', 'TitleMaster.csv', 'AgencyMaster.csv']
    payroll_files = ['nycpayroll_2021.csv','nycpayroll_2020.csv']

    return s3_client, engine, s3_bucket, s3_prefix, table_schemas, attributes, master_files, payroll_files


def process_master_data():
    """
    Process and stage master data files.
    """
    transform_master_data(master_files, table_schemas, s3_client, s3_bucket, s3_prefix, engine)

def process_transactional_data():
    """
    Process and stage transactional payroll data files.
    """
    transform_transactional_data(payroll_files, table_schemas, attributes, s3_client, s3_bucket, s3_prefix, engine)

def main():
    """
    Main function to orchestrate the ETL process.
    """
    try:
        # Step 1: Load environment variables and setup
        load_env_and_setup()
        
        # Step 2: Process master data
        process_master_data()
        
        # Step 3: Process transactional data
        process_transactional_data()
        
        # Step 4: Trigger DBT for final transformations and loading
        dbt_trigger()
        logging.info("ETL process completed successfully.")

    except Exception as e:
        logging.error(f"ETL process failed: {e}")
        raise

if __name__ == "__main__":
    main()