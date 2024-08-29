-- models/staging/stg_fact_payroll.sql
WITH cleaned AS (
    SELECT
        PayrollNumber::INT,
        EmployeeID::INT,
        FiscalYear::INT,
        BaseSalary::DECIMAL(10, 2),
        RegularHours::DECIMAL(10, 2),
        RegularGrossPaid::DECIMAL(10, 2),
        OTHours::DECIMAL(10, 2),
        TotalOTPaid::DECIMAL(10, 2),
        TotalOtherPay::DECIMAL(10, 2),
        WorkLocationBorough::VARCHAR(20)
    FROM {{ source('stg', 'staging_fact_payroll') }}
)
SELECT * FROM cleaned;
