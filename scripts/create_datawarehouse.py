import boto3
from dotenv import load_dotenv
import os

# Load credentials from .env
load_dotenv(override=True)

# Initialize the Redshift Data API client
client = boto3.client('redshift-data')

# Set your Redshift Serverless parameters
database_name = os.getenv('database')
workgroup_name = os.getenv('workgroup_name')

# SQL commands to execute
sql_commands = """
-- Create schemas
CREATE SCHEMA IF NOT EXISTS stg;
CREATE SCHEMA IF NOT EXISTS edw;

-- Create DimEmployee Table
CREATE TABLE edw.dim_employee (
    EmployeeID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    LeaveStatusasofJune30 VARCHAR(10)
);

-- Create DimAgency Table
CREATE TABLE edw.dim_agency (
    AgencyID INT PRIMARY KEY,
    AgencyName VARCHAR(100),
    AgencyStartDate DATE
);

-- Create DimTitle Table
CREATE TABLE edw.dim_title (
    TitleCode INT PRIMARY KEY,
    TitleDescription TEXT
);

-- Create DimDate Table
CREATE TABLE edw.dim_date (
    DateID INT PRIMARY KEY,
    Date DATE NOT NULL,
    Year INT,
    Month INT,
    Day INT,
    FiscalYear INT,
    Quarter INT,
    MonthName VARCHAR(20),
    DayOfWeek VARCHAR(20)
);

-- Create FactPayroll Table
CREATE TABLE edw.fact_payroll (
    PayrollID INT PRIMARY KEY DEFAULT nextval('factpayroll_seq'),
    EmployeeID INT,
    AgencyID INT,
    TitleCode INT,
    DateID INT,
    PayrollNumber INT,
    PayBasis VARCHAR(50),
    WorkLocationBorough VARCHAR(50),
    RegularHours DECIMAL(10, 2),
    BaseSalary DECIMAL(10, 2),
    RegularGrossPaid DECIMAL(10, 2),
    OTHours DECIMAL(10, 2),
    TotalOTPaid DECIMAL(10, 2),
    TotalOtherPay DECIMAL(10, 2),
    FOREIGN KEY (EmployeeID) REFERENCES edw.dim_employee(EmployeeID),
    FOREIGN KEY (AgencyID) REFERENCES edw.dim_agency(AgencyID),
    FOREIGN KEY (TitleCode) REFERENCES edw.dim_title(TitleCode),
    FOREIGN KEY (DateID) REFERENCES edw.dim_date(DateID)
);

-- Create payroll_aggregate_by_agency Table
CREATE TABLE edw.payroll_aggregate_by_agency (
    AgencyID INT,
    AgencyName VARCHAR(100),
    FiscalYear INT,
    TotalBaseSalary DECIMAL(10, 2),
    TotalRegularGrossPaid DECIMAL(10, 2),
    TotalOTHours DECIMAL(10, 2),
    TotalOTPaid DECIMAL(10, 2),
    TotalOtherPaid DECIMAL(10, 2),
    TotalSupplementalPay DECIMAL(10, 2),
    TotalEmployees INT,
    PRIMARY KEY (AgencyID, FiscalYear)
);

-- Create overtime_by_employee_and_agency Table
CREATE TABLE edw.overtime_by_employee_and_agency (
    EmployeeID INT,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    AgencyID INT,
    AgencyName VARCHAR(100),
    TotalOTHours DECIMAL(10, 2),
    TotalOTPaid DECIMAL(10, 2),
    PRIMARY KEY (EmployeeID, AgencyID)
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
