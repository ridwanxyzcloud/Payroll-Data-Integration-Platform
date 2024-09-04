# Use the official Airflow image with Python 3.9
FROM apache/airflow:2.9.2-python3.9

# Switch to root to install system dependencies
USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the airflow user before running pip install
USER airflow

# Copy and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy dbt project files
COPY dbt /opt/airflow/dbt

# Set environment variables for dbt
ENV DBT_PROFILES_DIR=/opt/airflow/dbt

# Copy Airflow configuration and DAGs
COPY airflow.cfg /opt/airflow/airflow.cfg
COPY dags /opt/airflow/dags

# Change ownership of the copied files using the numeric user and group IDs
USER root

# UID:GID
RUN chown -R 50000:50000 /opt/airflow/

# Switch back to the airflow user
USER airflow

# Set the entrypoint to the Airflow command
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["airflow", "webserver"]
