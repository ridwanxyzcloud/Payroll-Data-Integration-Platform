from io import StringIO
import os
import pandas as pd
import boto3
from prometheus_client import Gauge
import logging





def initialize_s3_client(aws_region, aws_access_key_id, aws_secret_access_key):
    return boto3.client(
        's3',
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )


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
