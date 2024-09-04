WITH source_data AS (
    SELECT
        a.AgencyID,
        a.AgencyName,
        f.FiscalYear,
        SUM(f.BaseSalary) AS TotalBaseSalary,
        SUM(f.RegularGrossPaid) AS TotalRegularGrossPaid,
        SUM(f.OTHours) AS TotalOTHours,
        SUM(f.TotalOTPaid) AS TotalOTPaid,
        SUM(f.TotalOtherPay) AS TotalOtherPay,
        SUM(f.TotalOTPaid + f.TotalOtherPay) AS TotalSupplementalPay,
        COUNT(DISTINCT f.EmployeeID) AS TotalEmployees
    FROM
        {{ source('stg', 'staging_fact_payroll') }} f  -- Aggregating directly from the source
    JOIN
        {{ source('stg', 'staging_dim_agency') }} a
    ON
        f.AgencyID = a.AgencyID
    GROUP BY
        a.AgencyID, a.AgencyName, f.FiscalYear
)

SELECT
    AgencyID,
    AgencyName,
    FiscalYear,
    TotalBaseSalary,
    TotalRegularGrossPaid,
    TotalOTHours,
    TotalOTPaid,
    TotalOtherPay,
    TotalSupplementalPay,
    TotalEmployees
FROM source_data
