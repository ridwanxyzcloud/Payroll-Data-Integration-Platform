import subprocess
import logging
import os

def dbt_trigger():
    """
    Trigger the DBT process for further transformations and loading data into the final warehouse.
    """
    # Change directory to where the dbt project is located
    os.chdir('/opt/airflow/dbt')

    # Run the dbt command
    result = subprocess.run(['dbt', 'run', '--profiles-dir', '.'], capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode != 0:
        raise Exception(f"dbt command failed: {result.stderr}")
        logging.error("DBT run failed")
    else:
        print(f"dbt command succeeded")
        logging.info("DBT run successful")