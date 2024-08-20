FROM python:3.9-slim

RUN pip install --no-cache-dir \
    apache-airflow==2.1.4 \
    boto3 \
    pandas \
    sqlalchemy \
    dbt-core \
    dbt-redshift

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./airflow/dags /usr/local/airflow/dags
COPY ./airflow/plugins /usr/local/airflow/plugins
COPY ./airflow/config /usr/local/airflow/config

WORKDIR /usr/local/airflow
