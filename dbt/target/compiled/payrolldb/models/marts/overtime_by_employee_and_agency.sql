WITH source_data AS (
    SELECT
        EmployeeID,
        AgencyID,
        TitleCode,
        SUM(OTHours) AS TotalOTHours,
        SUM(TotalOTPaid) AS TotalOTPaid
    FROM
        "payrolldb"."edw_edw"."fact_payroll"
    GROUP BY
        EmployeeID, AgencyID, TitleCode
)

SELECT
    EmployeeID,
    AgencyID,
    TitleCode,
    TotalOTHours,
    TotalOTPaid
FROM source_data