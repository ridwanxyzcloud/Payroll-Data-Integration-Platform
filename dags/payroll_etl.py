from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import logging
from helpers.logging_utils import setup_logging
from scripts.extract import extract_data
from scripts.transform import transform_master_data, transform_transactional_data
from scripts.load import load_master_data, load_transactional_data
from helpers.db_utils import create_db_engine
from helpers.metrics import start_metrics_server
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv(override=True)

# Setup logging
setup_logging()

# Start Prometheus metrics server
start_metrics_server(port=8000)

# Database configuration
db_url = 'postgresql://username:password@redshift-cluster-url:5439/nyc_payroll'
engine = create_db_engine(db_url)

# File definitions
master_files = ['EmpMaster.csv', 'TitleMaster.csv', 'AgencyMaster.csv']
payroll_files = ['nycpayroll_2020.csv', 'nycpayroll_2021.csv']
master_table_names = ['DimEmployee', 'DimTitle', 'DimAgency']
master_columns = [
    ['EmployeeID', 'LastName', 'FirstName'],
    ['TitleCode', 'TitleDescription'],
    ['AgencyID', 'AgencyName']
]

transactional_columns = [
    'FiscalYear', 'PayrollNumber', 'AgencyID', 'AgencyName', 'EmployeeID', 'LastName', 'FirstName',
    'AgencyStartDate', 'WorkLocationBorough', 'TitleCode', 'TitleDescription', 'LeaveStatusasofJune30',
    'BaseSalary', 'PayBasis', 'RegularHours', 'RegularGrossPaid', 'OTHours', 'TotalOTPaid', 'TotalOtherPay'
]

dim_columns = [
    ['EmployeeID', 'LastName', 'FirstName', 'LeaveStatusasofJune30'],
    ['TitleCode', 'TitleDescription'],
    ['AgencyID', 'AgencyName', 'AgencyStartDate']
]
required_columns = [
        'FiscalYear', 'PayrollNumber', 'AgencyID', 'EmployeeID', 'WorkLocationBorough',
        'TitleCode', 'BaseSalary', 'PayBasis', 'RegularHours', 'RegularGrossPaid',
        'OTHours', 'TotalOTPaid', 'TotalOtherPay'
    ]



# AWS and S3 configuration
s3_bucket = os.getenv("s3_bucket")
s3_prefix = os.getenv("s3_prefix")
aws_region = os.getenv("aws_region")
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")


# Define default_args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Initialize DAG
dag = DAG(
    'nyc_payroll_etl',
    default_args=default_args,
    description='NYC Payroll ETL Pipeline',
    schedule_interval='@daily',
)

def ingest_master_data():
    logging.info("Starting master data ingestion")
    for file_name, table_name, dim_col in zip(master_files, master_table_names, dim_columns):
        df = extract_data(file_name)
        df_transformed = transform_master_data(df, dim_col)
        load_master_data(df_transformed, table_name, engine)
        logging.info(f"Completed loading {file_name} into {table_name}")

def ingest_transactional_data():
    logging.info("Starting transactional data ingestion")
    for file_name in payroll_files:
        df = extract_data(file_name)
        df_transformed = transform_transactional_data(df, engine)
        load_transactional_data(df_transformed, engine)
        logging.info(f"Completed loading {file_name} into FactPayroll")

def trigger_dbt():
    logging.info("Triggering DBT")
    try:
        import os
        os.system('dbt run --profiles-dir /path/to/your/dbt/profiles --project-dir /path/to/your/dbt/project')
        logging.info("DBT run completed successfully")
    except Exception as e:
        logging.error(f"Failed to trigger DBT: {str(e)}")
        raise

# Airflow tasks
t1 = PythonOperator(
    task_id='extract_transform_master_data',
    python_callable=ingest_master_data,
    dag=dag
)

t2 = PythonOperator(
    task_id='extract_transform_transactional_data',
    python_callable=ingest_transactional_data,
    dag=dag
)

t3 = PythonOperator(
    task_id='trigger_dbt',
    python_callable=trigger_dbt,
    dag=dag
)

# Define task dependencies
t1 >> t2 >> t3
