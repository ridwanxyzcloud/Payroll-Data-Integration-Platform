from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import logging
import pandas as pd
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
    """
    Creates a SQLAlchemy engine for Redshift using credentials from environment variables.

    :return: SQLAlchemy engine object if successful, otherwise None.
    """
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
    """
    Stages data to a Redshift table in the 'stg' schema.

    :param engine: SQLAlchemy engine object connected to Redshift.
    :param df: Pandas DataFrame containing the data to stage.
    :param table_name: Name of the table to stage data to.
    :return: None
    """
    if engine is None:
        logging.error("Engine is not initialized.")
        return

    staging_table_name = f"staging_{table_name.lower()}"
    try:
        df.to_sql(staging_table_name, engine, schema='stg', if_exists='replace', index=False)
        logging.info(f"Data successfully staged to {staging_table_name}.")
    except Exception as e:
        logging.error(f"Failed to stage data to {staging_table_name}: {str(e)}")


def read_table(engine, table_name):
    """
    Reads data from a Redshift table into a Pandas DataFrame.

    :param engine: SQLAlchemy engine object connected to Redshift.
    :param table_name: Name of the table to read data from.
    :return: DataFrame containing the table data, or None if reading fails.
    """
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


def redshift_engine2():

    if not all([username, password, host, port, database]):
        logging.error("Missing required environment variables for Redshift connection.")
        return None

    # Use the PostgresSQL dialect for Redshift
    db_url = f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}'

    try:
        # Create and return the SQLAlchemy engine
        engine = create_engine(db_url)
        logging.info("Successfully created Redshift engine.")
        return engine
    except Exception as e:
        logging.error(f"Failed to create engine: {str(e)}")
        return None

