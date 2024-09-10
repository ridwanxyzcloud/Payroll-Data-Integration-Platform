import sys
import os
from datetime import timedelta

# project root
sys.path.append('/opt/airflow')

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import pandas as pd
import os
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
    start_metrics_server, files_extracted, rows_extracted, rows_transformed, rows_validated, 
    missing_values_detected, rows_staged, rows_processed, rows_cleaned, data_quality_issues
)
from scripts.dbt_run import dbt_trigger  # Import the dbt_trigger function

# Define the default_args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1
}

# Define the DAG
with DAG(
    'data_processing_dag',
    default_args=default_args,
    description='DAG for processing master and transactional data and running DBT transformations',
    schedule_interval=None,  # Use cron syntax for scheduling
    catchup=False,
) as dag:

    def load_env_and_setup():
        load_dotenv(override=True)

        # Start Prometheus metrics server
        start_metrics_server(port=8000)
        setup_logging()
        global s3_client, engine, s3_bucket, s3_prefix, table_schemas, attributes, master_files, payroll_files

        s3_client = get_s3_client()
        engine = redshift_engine()
        
        s3_bucket = os.getenv("s3_bucket")
        s3_prefix = os.getenv("s3_prefix")

        # Validate environment variables
        if not s3_bucket or not s3_prefix:
            logging.error("s3_bucket or s3_prefix environment variables are not set.")
            raise ValueError("s3_prefix or s3_prefix environment variables are not set.")
        
        master_files = ['EmpMaster.csv', 'TitleMaster.csv', 'AgencyMaster.csv']

        payroll_files = ['nycpayroll_2021.csv','nycpayroll_2020.csv']

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


    
    def process_master_data():
        master_files = ['EmpMaster.csv', 'TitleMaster.csv', 'AgencyMaster.csv']
        transform_master_data(master_files)

    def process_transactional_data():
        payroll_files = ['nycpayroll_2021.csv','nycpayroll_2020.csv']
        transform_transactional_data(payroll_files)

    # Initialize environment and setup task
    init_task = PythonOperator(
        task_id='init_env_and_setup',
        python_callable=load_env_and_setup,
    )

    # Task to transform and stage master data
    master_data_task = PythonOperator(
        task_id='transform_and_stage_master_data',
        python_callable=process_master_data,
    )

    # Task to transform and stage transactional data
    transactional_data_task = PythonOperator(
        task_id='transform_and_stage_transactional_data',
        python_callable=process_transactional_data,
    )

    # Task to trigger DBT for final transformations and load
    dbt_task = PythonOperator(
        task_id='dbt_run',
        python_callable=dbt_trigger,
    )

    # Define task dependencies
    init_task >> master_data_task >> transactional_data_task >> dbt_task
