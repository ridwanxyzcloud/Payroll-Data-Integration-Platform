import subprocess
import logging


logging.info("Data successfully staged.")

# Run DBT models to load data to EDW and create aggregate tables
try:
    subprocess.run(["dbt", "run"], check=True)
    logging.info("DBT run completed successfully.")
except subprocess.CalledProcessError as e:
    logging.error(f"DBT run failed: {str(e)}")

# Log metrics to Prometheus (pseudo-code, replace with actual Prometheus integration)
# prom_gauge.set(some_value)
logging.info("Metrics updated in Prometheus.")
