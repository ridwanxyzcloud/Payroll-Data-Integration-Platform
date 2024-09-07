import logging
from io import StringIO
import os
import pandas as pd
from helpers.metrics_server import (total_master_rows_extracted, total_transactional_rows_extracted, 
                              total_rows_extracted, master_files_count, transactional_files_count, 
                              total_files_count)


def extract_from_s3(s3_client, bucket, prefix, file_name):
    """
    Extracts a CSV file from an S3 bucket and loads it into a Pandas DataFrame.

    Parameters:
    -----------
    s3_client : boto3.client
        The boto3 S3 client used to interact with S3.
    bucket : str
        The name of the S3 bucket.
    prefix : str
        The prefix (folder path) in the S3 bucket where the file is located.
    file_name : str
        The name of the file to be extracted from S3.

    Returns:
    --------
    pd.DataFrame
        A Pandas DataFrame containing the data from the extracted CSV file.

    Raises:
    -------
    Exception
        If the extraction process fails, an exception is logged and re-raised.
    """
    try:
        logging.info(f"Extracting {file_name} from S3")
        obj = s3_client.get_object(Bucket=bucket, Key=prefix + file_name)
        df = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))
        
        total_rows_extracted.inc(len(df))
        total_files_count.inc()

        return df
    except Exception as e:
        logging.error(f"Failed to extract {file_name}: {str(e)}")
        raise


def extract_data(file_name, s3_client, s3_bucket, s3_prefix):
    """
    Extracts data from an S3 bucket using the provided S3 client, bucket, and prefix.

    Parameters:
    -----------
    file_name : str
        The name of the file to be extracted from S3.
    s3_client : boto3.client
        The boto3 S3 client used to interact with S3.
    s3_bucket : str
        The name of the S3 bucket.
    s3_prefix : str
        The prefix (folder path) in the S3 bucket where the file is located.

    Returns:
    --------
    pd.DataFrame
        A Pandas DataFrame containing the data from the extracted CSV file.
    """
    return extract_from_s3(s3_client, s3_bucket, s3_prefix, file_name)

