from io import StringIO
import os
import pandas as pd
import boto3
from prometheus_client import Gauge
import logging


def initialize_s3_client(aws_region, aws_access_key_id, aws_secret_access_key):
    """
    Initializes and returns an S3 client using the specified AWS credentials.

    Args:
        aws_region (str): The AWS region where the S3 service is hosted.
        aws_access_key_id (str): The AWS access key ID for authentication.
        aws_secret_access_key (str): The AWS secret access key for authentication.

    Returns:
        boto3.client: A configured S3 client instance.

    """
    return boto3.client(
        's3',
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )


def extract_from_s3(s3_client, bucket, prefix, file_name):
    """
    Extracts a CSV file from an S3 bucket and returns it as a pandas DataFrame.

    Args:
        s3_client (boto3.client): An S3 client instance.
        bucket (str): The name of the S3 bucket from which to retrieve the file.
        prefix (str): The prefix path within the bucket where the file is located.
        file_name (str): The name of the file to retrieve.

    Returns:
        pandas.DataFrame: A DataFrame containing the contents of the CSV file.

    Raises:
        Exception: If the file cannot be retrieved or an error occurs during extraction.

    """
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
