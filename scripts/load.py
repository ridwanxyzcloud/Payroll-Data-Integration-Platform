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


def ingest_master_data():
    logging.info(f"Ingesting master data")
    s3_bucket = 'your-s3-bucket-name'
    s3_prefix = 'your-folder-prefix/'
    master_files = ['EmpMaster.csv', 'TitleMaster.csv', 'AgencyMaster.csv']
    master_table_names = ['DimEmployee', 'DimTitle', 'DimAgency']
    dim_columns = [
        ['EmployeeID', 'LastName', 'FirstName', 'LeaveStatusasofJune30'],
        ['TitleCode', 'TitleDescription'],
        ['AgencyID', 'AgencyName', 'AgencyStartDate']
    ]

    for file_name, table_name, dim_col in zip(master_files, master_table_names, dim_columns):
        df = extract.extract_from_s3(s3_bucket, s3_prefix, file_name)
        df_transformed = transform.transform_master_data(df, dim_col)
        stage_data(df_transformed, table_name)


def ingest_transactional_data():
    logging.info(f"Ingesting transactional data")
    s3_bucket = 'your-s3-bucket-name'
    s3_prefix = 'your-folder-prefix/'
    payroll_files = ['nycpayroll_2020.csv', 'nycpayroll_2021.csv']

    create_fact_table()

    for file_name in payroll_files:
        df = extract.extract_from_s3(s3_bucket, s3_prefix, file_name)
        df_transformed = transform.transform_transactional_data(df, engine)
        stage_data(df_transformed, 'FactPayroll')
