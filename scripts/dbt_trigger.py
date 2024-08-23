import subprocess
import logging

# Stage the data
stage_data(engine, dim_employee_df, 'dim_employee')
stage_data(engine, dim_agency_df, 'dim_agency')
stage_data(engine, dim_title_df, 'dim_title')
stage_data(engine, fact_payroll_df, 'fact_payroll')

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
