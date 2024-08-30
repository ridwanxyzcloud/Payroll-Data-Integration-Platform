WITH cleaned AS (
    SELECT
        AgencyID::INT,
        INITCAP(AgencyName) AS AgencyName,
        COALESCE(AgencyStartDate::DATE, '1900-01-01') AS AgencyStartDate
    FROM {{ source('stg', 'staging_dim_agency') }}
)
SELECT * FROM cleaned