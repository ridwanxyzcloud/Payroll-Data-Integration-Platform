from helpers.s3_utils import extract_from_s3, s3_client
from helpers.metrics import files_extracted
import logging
from io import StringIO
import pandas as pd
from helpers.s3_utils import s3_client



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

        # Update metrics
        files_extracted.inc()  # Increment the count of files extracted

        return df
    except Exception as e:
        logging.error(f"Failed to extract {file_name}: {str(e)}")
        raise


def extract_data(file_name):
    """
    Extracts data from an S3 bucket using predefined S3 client, bucket, and prefix.

    This function serves as a wrapper around `extract_from_s3` and uses globally defined
    `s3_client`, `s3_bucket`, and `s3_prefix`.

    Parameters:
    -----------
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
    return extract_from_s3(s3_client, s3_bucket, s3_prefix, file_name)
