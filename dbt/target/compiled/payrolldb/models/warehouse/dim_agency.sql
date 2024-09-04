WITH transformed AS (
    SELECT DISTINCT
        -- Directly cast and transform the source data
        AgencyID::INT AS AgencyID,
        INITCAP(AgencyName) AS AgencyName,
        COALESCE(AgencyStartDate::DATE, '1900-01-01') AS AgencyStartDate
    FROM "payrolldb"."stg"."staging_dim_agency"
)

SELECT
    AgencyID,
    AgencyName,
    AgencyStartDate
FROM transformed


    WHERE NOT EXISTS (
        SELECT 1
        FROM "payrolldb"."edw_edw"."dim_agency"
        WHERE AgencyID = transformed.AgencyID
    )
