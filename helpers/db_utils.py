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
    """
    Creates and returns a SQLAlchemy engine for connecting to an Amazon Redshift database.

    The function retrieves required connection parameters (username, password, host, port,
    database) from environment variables. If any of these variables are missing, it logs
    an error and returns None. If all variables are present, it constructs the Redshift
    database URL and attempts to create a SQLAlchemy engine.

    Returns:
    --------
    engine : sqlalchemy.engine.base.Engine or None
        A SQLAlchemy engine object for the Redshift connection if successful, otherwise None.

    Logs:
    -----
    - Logs an error if required environment variables are missing.
    - Logs the success or failure of the engine creation.

    Raises:
    -------
    Exception:
        Logs any exceptions that occur during the engine creation process, and returns None.

    Example Usage:
    --------------
    engine = redshift_engine()
    if engine is not None:
        # Proceed with using the engine to connect to the Redshift database
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
    Stages data to an Amazon Redshift database by uploading a DataFrame to a staging table.

    This function uses the provided SQLAlchemy engine to upload a DataFrame (`df`) to a
    specified staging table in the Redshift database. The staging table name is derived
    by prefixing the given `table_name` with 'staging_' and converting it to lowercase.
    The data is uploaded to the 'stg' schema and replaces any existing data in the table.

    Parameters:
    -----------
    engine : sqlalchemy.engine.base.Engine
        The SQLAlchemy engine used to connect to the Redshift database. If `engine` is None,
        the function logs an error and exits.

    df : pd.DataFrame
        The DataFrame containing the data to be staged in Redshift.

    table_name : str
        The name of the target table in Redshift. The actual staging table name will be
        prefixed with 'staging_'.

    Logs:
    -----
    - Logs an error if the engine is not initialized.
    - Logs the success or failure of the data staging process.

    Raises:
    -------
    Exception:
        Logs any exceptions that occur during the data staging process.

    Example Usage:
    --------------
    engine = redshift_engine()
    if engine is not None:
        stage_data(engine, df, 'target_table')
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
