import boto3
from dotenv import load_dotenv
import os

# Load credentials from .env
load_dotenv(override=True)

# Initialize the Redshift Data API client
client = boto3.client('redshift-data')

# Set your Redshift Serverless parameters
database_name = os.getenv('database_name')
workgroup_name = os.getenv('workgroup_name')

# SQL commands to execute
sql_commands = """
-- Create schemas
CREATE SCHEMA IF NOT EXISTS stg;
CREATE SCHEMA IF NOT EXISTS edw;

-- Create tables
CREATE TABLE edw.DimEmployee (
    EmployeeID INT PRIMARY KEY,
    LastName VARCHAR(50),
    FirstName VARCHAR(50),
    LeaveStatusasofJune30 VARCHAR(10)
);

CREATE TABLE edw.DimAgency (
    AgencyID INT PRIMARY KEY,
    AgencyName VARCHAR(100),
    AgencyStartDate DATE
);

CREATE TABLE edw.DimTitle (
    TitleCode INT PRIMARY KEY,
    TitleDescription TEXT
);

CREATE TABLE edw.FactPayroll (
    PayrollID INT PRIMARY KEY,
    EmployeeID INT REFERENCES edw.DimEmployee(EmployeeID),
    AgencyID INT REFERENCES edw.DimAgency(AgencyID),
    TitleCode INT REFERENCES edw.DimTitle(TitleCode),
    FiscalYear INT,
    PayrollNumber INT,
    PayBasis VARCHAR(20),
    WorkLocationBorough VARCHAR(20),
    RegularHours DECIMAL(10, 2),
    BaseSalary DECIMAL(10, 2),
    RegularGrossPaid DECIMAL(10, 2),
    OTHours DECIMAL(10, 2),
    TotalOTPaid DECIMAL(10, 2),
    TotalOtherPaid DECIMAL(10, 2)
);
"""

def execute_sql_commands():
    try:
        # Execute SQL commands
        response = client.execute_statement(
            WorkgroupName=workgroup_name,
            Sql=sql_commands,
            Database=database_name
            # DbUser parameter is removed
        )
        statement_id = response['Id']
        print(f"SQL commands executed successfully with statement ID: {statement_id}")
    except Exception as e:
        print(f"Error executing SQL commands: {e}")

if __name__ == "__main__":
    execute_sql_commands()
