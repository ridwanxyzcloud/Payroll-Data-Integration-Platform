-- create_tables.sql
CREATE TABLE DimEmployee (
    EmployeeID INT PRIMARY KEY,
    LastName VARCHAR(50),
    FirstName VARCHAR(50),
    LeaveStatusasofJune30 VARCHAR(10)
);

CREATE TABLE DimAgency (
    AgencyID INT PRIMARY KEY,
    AgencyName VARCHAR(100),
    AgencyStartDate DATE
);

CREATE TABLE DimTitle (
    TitleCode INT PRIMARY KEY,
    TitleDescription TEXT
);

CREATE TABLE FactPayroll (
    PayrollID INT PRIMARY KEY,
    EmployeeID INT REFERENCES DimEmployee(EmployeeID),
    AgencyID INT REFERENCES DimAgency(AgencyID),
    TitleCode INT REFERENCES DimTitle(TitleCode),
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
