WITH cleaned AS (
    SELECT
        TitleCode::INT,
        COALESCE(TitleDescription, '')::TEXT AS TitleDescription
    FROM {{ source('stg', 'staging_dim_title') }}
)
SELECT * FROM cleaned