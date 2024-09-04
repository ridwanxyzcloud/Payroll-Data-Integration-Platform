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
    PayrollID VARCHAR(32) PRIMARY KEY,  -- UUIDs as VARCHAR
    PayrollNumber INT,
    EmployeeID INT,
    AgencyID INT,
    TitleCode INT,
    DateID INT,
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
CREATE TABLE marts.payroll_aggregate_by_agency (
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
    PRIMARY KEY (AgencyID, FiscalYear),
    FOREIGN KEY (AgencyID) REFERENCES edw.dim_agency(AgencyID)
);

-- Create overtime_by_employee_and_agency Table
CREATE TABLE marts.overtime_by_employee_and_agency (
    EmployeeID INT,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    AgencyID INT,
    AgencyName VARCHAR(100),
    TotalOTHours DECIMAL(10, 2),
    TotalOTPaid DECIMAL(10, 2),
    PRIMARY KEY (EmployeeID, AgencyID),
    FOREIGN KEY (EmployeeID) REFERENCES edw.dim_employee(EmployeeID),
    FOREIGN KEY (AgencyID) REFERENCES edw.dim_agency(AgencyID)
);
