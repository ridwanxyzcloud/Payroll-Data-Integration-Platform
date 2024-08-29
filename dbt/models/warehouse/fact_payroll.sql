-- models/warehouse/fact_payroll.sql
{{ config(
    materialized='incremental',
    unique_key='PayrollID',
    incremental_strategy='merge'
) }}

WITH fiscal_year_lookup AS (
    SELECT DateID, FiscalYear
    FROM {{ ref('dim_date') }}
)

, source_data AS (
    SELECT
        nextval('factpayroll_seq') AS PayrollID,
        f.EmployeeID,
        f.AgencyID,
        f.TitleCode,
        fy.DateID AS DateID,
        f.PayrollNumber,
        f.PayBasis,
        f.WorkLocationBorough,
        f.RegularHours,
        f.BaseSalary,
        f.RegularGrossPaid,
        f.OTHours,
        f.TotalOTPaid,
        f.TotalOtherPay
    FROM {{ ref('stg_fact_payroll') }} f
    LEFT JOIN fiscal_year_lookup fy
    ON f.FiscalYear = fy.FiscalYear
)

SELECT * FROM source_data

{% if is_incremental() %}
    WHERE NOT EXISTS (
        SELECT 1
        FROM {{ this }}
        WHERE EmployeeID = source_data.EmployeeID
        AND AgencyID = source_data.AgencyID
        AND TitleCode = source_data.TitleCode
        AND DateID = source_data.DateID
    )
{% endif %}
