import os
import logging


def trigger_dbt():
    logging.info(f"Triggering DBT")
    try:
        os.system('dbt run --profiles-dir /path/to/your/dbt/profiles --project-dir /path/to/your/dbt/project')
    except Exception as e:
        logging.error(f"Failed to trigger DBT: {str(e)}")
        raise

