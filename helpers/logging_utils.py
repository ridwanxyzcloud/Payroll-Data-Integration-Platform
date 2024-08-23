import logging


def setup_logging():
    """
    Configures the logging settings for the ETL pipeline.

    This function sets up the logging configuration for the application, defining the log
    level, format, and handlers. Logs are written both to a file and the console.

    Logging Configuration:
    ----------------------
    - **Level**: INFO. Logs all messages at the INFO level and above.
    - **Format**: Each log message includes the timestamp, logger name, log level, and message.
    - **Handlers**:
        - **FileHandler**: Logs are written to a file located at `logs/etl_pipeline.log`.
        - **StreamHandler**: Logs are also output to the console (standard output).

    Example Usage:
    --------------
    setup_logging()
    logging.info("ETL pipeline started.")
    """

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/etl_pipeline.log"),
            logging.StreamHandler()
        ]
    )
