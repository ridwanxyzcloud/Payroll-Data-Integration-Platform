from helpers.s3_utils import extract_from_s3, initialize_s3_client
import logging
from io import StringIO
import pandas as pd

# Define a gauge for monitoring S3 extraction
files_extracted = Gauge('s3_files_extracted', 'Number of files extracted from S3')

# s3 client
s3_client = initialize_s3_client(aws_region, aws_access_key_id, aws_secret_access_key)

def extract_from_s3(s3_client, bucket, prefix, file_name):
    try:
        logging.info(f"Extracting {file_name} from S3")
        obj = s3_client.get_object(Bucket=bucket, Key=prefix + file_name)
        df = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))

        # Update metrics
        files_extracted.inc()  # Increment the count of files extracted

        return df
    except Exception as e:
        logging.error(f"Failed to extract {file_name}: {str(e)}")
        raise

def extract_data(file_name):
    return extract_from_s3(s3_client, s3_bucket, s3_prefix, file_name)
