from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import logging
from scripts.extract import extract_data
from scripts.transform import transform_master_data, transform_transactional_data
from scripts.load import load_master_data, load_transactional_data
from helpers.logging_utils import setup_logging
from helpers.db_utils import create_db_engine

# Setup logging
setup_logging()

# Define default_args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Initialize DAG
dag = DAG(
    'nyc_payroll_etl',
    default_args=default_args,
    description='NYC Payroll ETL Pipeline',
    schedule_interval=timedelta(days=1),
)

# Database connection
db_url = 'postgresql+psycopg2://user:password@db:5432/payroll_db'
engine = create_db_engine(db_url)

def run_etl():
    # Extract
    master_data = extract_data('master_data.csv')
    transactional_data = extract_data('transactional_data.csv')

    # Transform
    transformed_master_data = transform_master_data(master_data, ['EmployeeID', 'AgencyID'])
    transformed_transactional_data = transform_transactional_data(transactional_data, engine)

    # Load
    load_master_data(transformed_master_data, 'DimMaster', engine)
    load_transactional_data(transformed_transactional_data, engine)

# Define the ETL task
etl_task = PythonOperator(
    task_id='run_etl',
    python_callable=run_etl,
    dag=dag,
)

etl_task
