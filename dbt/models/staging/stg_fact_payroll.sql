-- models/staging/stg_fact_payroll.sql
select
    PayrollNumber,
    EmployeeID,
    FiscalYear,
    BaseSalary,
    RegularHours,
    RegularGrossPaid,
    OTHours,
    TotalOTPaid,
    TotalOtherPay,
    WorkLocationBorough
from {{ source('stg', 'staging_fact_payroll') }}
