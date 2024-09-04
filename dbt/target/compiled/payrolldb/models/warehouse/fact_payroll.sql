WITH cleaned AS (
    SELECT DISTINCT
        -- Generate a pseudo-UUID as a VARCHAR
        md5(random()::text || getdate()::text) AS PayrollID,  -- Using MD5 hash as UUID substitute
        PayrollNumber::INT AS PayrollNumber,
        EmployeeID::INT AS EmployeeID,
        AgencyID::INT AS AgencyID,
        TitleCode::INT AS TitleCode,
        FiscalYear::INT AS FiscalYear,
        BaseSalary::DECIMAL(10, 2) AS BaseSalary,
        RegularHours::DECIMAL(10, 2) AS RegularHours,
        RegularGrossPaid::DECIMAL(10, 2) AS RegularGrossPaid,
        OTHours::DECIMAL(10, 2) AS OTHours,
        TotalOTPaid::DECIMAL(10, 2) AS TotalOTPaid,
        TotalOtherPay::DECIMAL(10, 2) AS TotalOtherPay,
        WorkLocationBorough::VARCHAR(20) AS WorkLocationBorough
    FROM "payrolldb"."stg"."staging_fact_payroll"
    WHERE PayrollNumber IS NOT NULL  -- Filter out rows where essential fields are null
),

fiscal_year_lookup AS (
    SELECT DateID, FiscalYear
    FROM "payrolldb"."edw"."dim_date"
)

SELECT DISTINCT
    c.PayrollID,
    c.PayrollNumber,
    c.EmployeeID,
    c.AgencyID,
    c.TitleCode,
    fy.DateID AS DateID,
    c.BaseSalary,
    c.RegularHours,
    c.RegularGrossPaid,
    c.OTHours,
    c.TotalOTPaid,
    c.TotalOtherPay,
    c.WorkLocationBorough
FROM cleaned c
LEFT JOIN fiscal_year_lookup fy
    ON c.FiscalYear = fy.FiscalYear


    WHERE NOT EXISTS (
        SELECT 1
        FROM "payrolldb"."edw_edw"."fact_payroll" AS existing
        WHERE existing.PayrollID = c.PayrollID
    )
