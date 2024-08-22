from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import pandas as pd
from snowflake.sqlalchemy import URL as URL_sn
import logging
from dotenv import load_dotenv
import os

# Load credentials from .env file
load_dotenv(override=True)

username = os.getenv('admin_user')
password = os.getenv('admin_password')
host = os.getenv('redshift_host')
port = os.getenv('redshift_port')
database = os.getenv('database')


def redshift_engine():

    if not all([username, password, host, port, database]):
        logging.error("Missing required environment variables for Redshift connection.")
        return None

    db_url = f'redshift+psycopg2://{username}:{password}@{host}:{port}/{database}'

    try:
        engine = create_engine(db_url)
        logging.info("Successfully created Redshift engine.")
        return engine
    except Exception as e:
        logging.error(f"Failed to create engine: {str(e)}")
        return None


def stage_data(engine, df, table_name):
    if engine is None:
        logging.error("Engine is not initialized.")
        return

    staging_table_name = f"staging_{table_name.lower()}"
    try:
        df.to_sql(staging_table_name, engine, schema='stg', if_exists='replace', index=False)
        logging.info(f"Data successfully staged to {staging_table_name}.")
    except Exception as e:
        logging.error(f"Failed to stage data to {staging_table_name}: {str(e)}")



def snowflake_engine():

    '''
    constructs a snowflake engine object for snowflake DB from .env file

    parameter: None

    Returns:
     - snowflake-connector engine (sqlalchemy.Engine)
    '''

    # create engine for snowflake
    try:
        # Create Snowflake URL
        snowflake_url = URL_sn(
            user=os.getenv('sn_user'),
            password=os.getenv('sn_password'),
            account=os.getenv('sn_account_identifier'),
            database=os.getenv('sn_database'),
            schema=os.getenv('sn_schema'),
            warehouse=os.getenv('sn_warehouse'),
            role=os.getenv('sn_role')
        )

        # Create SQLAlchemy engine and return it
        engine = create_engine(snowflake_url)
        return engine

    except Exception as e:
        print(f"Error creating Snowflake engine: {e}")
        return None

def read_table(engine, table_name):
    if engine is None:
        logging.error("Engine is not initialized.")
        return None

    try:
        df = pd.read_sql_table(table_name, engine)
        logging.info(f"Successfully read table {table_name}.")
        return df
    except Exception as e:
        logging.error(f"Failed to read table {table_name}: {str(e)}")
        return None
