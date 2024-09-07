import logging
from prometheus_client import Gauge, Counter, start_http_server

# File Counts
master_files_count = Gauge('master_files_count', 'Total number of master files processed')
transactional_files_count = Gauge('transactional_files_count', 'Total number of transactional files processed')
total_files_count = Gauge('total_files_count', 'Total number of files processed (master + transactional)')

# Metrics for Data Extraction
total_master_rows_extracted = Gauge('total_master_rows_extracted', 'Total number of master rows extracted from S3')
total_transactional_rows_extracted = Gauge('total_transactional_rows_extracted', 'Total number of transactional rows extracted from S3')
total_rows_extracted = Gauge('total_rows_extracted', 'Total number of rows extracted from S3')

# Metrics for Data Validation and Cleaning
total_master_rows_validated = Gauge('total_master_rows_validated', 'Total number of master rows validated')
total_master_rows_cleaned = Gauge('total_master_rows_cleaned', 'Total number of master rows cleaned')
missing_master_values_detected = Gauge('missing_master_values_detected', 'Number of missing values detected in master data')
total_transactional_rows_validated = Gauge('total_transactional_rows_validated', 'Total number of transactional rows validated')
total_transactional_rows_cleaned = Gauge('total_transactional_rows_cleaned', 'Total number of transactional rows cleaned')
missing_transactional_values_detected = Gauge('missing_transactional_values_detected', 'Number of missing values detected in transactional data')

data_quality_issues_master = Counter('data_quality_issues_master', 'Number of data quality issues encountered in master data')
data_quality_issues_transactional = Counter('data_quality_issues_transactional', 'Number of data quality issues encountered in transactional data')

# Metrics for Data Transformation
total_rows_transformed = Gauge('total_rows_transformed', 'Total number of rows transformed (validated and cleaned)')

# Metrics for Data Ingestion
total_master_rows_ingested = Gauge('total_master_rows_ingested', 'Total number of master rows ingested into staging')
total_transactional_rows_ingested = Gauge('total_transactional_rows_ingested', 'Total number of transactional rows ingested into staging')
total_rows_ingested = Gauge('total_rows_ingested', 'Total number of rows ingested into staging')

# Metrics for Data Loading (dbt_trigger)
total_master_rows_loaded = Gauge('total_master_rows_loaded', 'Total number of master rows loaded into data warehouse')
total_transactional_rows_loaded = Gauge('total_transactional_rows_loaded', 'Total number of transactional rows loaded into data warehouse')
total_rows_loaded = Gauge('total_rows_loaded', 'Total number of rows loaded into data warehouse')

# Start Prometheus metrics server
def start_metrics_server(port=8001):
    """
    Starts a Prometheus metrics server, handling cases where the port is already in use.

    :param port: The port on which the metrics server will listen (default is 8000).
    :return: None
    """
    try:
        start_http_server(port)
        logging.info(f"Prometheus metrics server started on port {port}")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            logging.error(f"Port {port} is already in use. Cannot start Prometheus metrics server.")
        else:
            logging.error(f"Error starting Prometheus metrics server: {e}")

def test_server(port=8001, max_retries=5):
    """
    Starts a Prometheus metrics server, handling cases where the port is already in use.

    :param port: The port on which the metrics server will listen (default is 8001).
    :param max_retries: Number of retries on port conflicts.
    :return: None
    """
    attempt = 0
    while attempt < max_retries:
        try:
            start_http_server(port)
            logging.info(f"Prometheus metrics server started on port {port}")
            break
        except OSError as e:
            if e.errno == 48:  # Address already in use
                logging.error(f"Port {port} is already in use. Retrying with another port...")
                port += 1  # Increment the port number and retry
            else:
                logging.error(f"Error starting Prometheus metrics server: {e}")
                break
        attempt += 1
    else:
        logging.error(f"Failed to start Prometheus metrics server after {max_retries} attempts.")
