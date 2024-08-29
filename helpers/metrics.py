from prometheus_client import Gauge, start_http_server

# Define Prometheus Gauges
files_extracted = Gauge('s3_files_extracted', 'Number of files extracted from S3')
rows_extracted = Gauge('etl_rows_extracted', 'Number of rows extracted from S3')
rows_transformed = Gauge('etl_rows_transformed', 'Number of rows transformed')
rows_validated = Gauge('etl_rows_validated', 'Number of rows passed data quality checks')
missing_values_detected = Gauge('etl_missing_values_detected', 'Number of missing values detected during validation')
rows_staged = Gauge('etl_rows_staged', 'Number of rows staged')
rows_processed = Gauge('data_rows_processed', 'Number of rows processed')
rows_cleaned = Gauge('data_rows_cleaned', 'Number of rows cleaned')
data_quality_issues = Gauge('data_quality_issues', 'Number of data quality issues encountered')


# Start Prometheus metrics server
def start_metrics_server(port=8000):
    """
    Starts a Prometheus metrics server.

    :param port: The port on which the metrics server will listen (default is 8000).
    :return: None
    """
    start_http_server(port)

