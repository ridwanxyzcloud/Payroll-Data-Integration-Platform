#import sys
import os

# PYTHONPATH for project directories
#project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#sys.path.append(project_root)

import subprocess
import logging


def dbt_trigger():
    """
    Trigger the DBT process for further transformations and loading data into the final warehouse.
    """
    # Change directory to where the dbt project is located
    os.chdir('./dbt')

    # Run the dbt command
    result = subprocess.run(['dbt', 'run', '--profiles-dir', '.'], capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode != 0:
        raise Exception(f"dbt command failed: {result.stderr}")
        logging.error("DBT run failed")
    else:
        print(f"dbt command succeeded")
        logging.info("DBT run successful")

dbt_trigger()