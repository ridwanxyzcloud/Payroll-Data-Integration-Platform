-- models/warehouse/dim_title.sql

WITH cleaned AS (
    SELECT DISTINCT
        TitleCode::INT AS TitleCode,
        COALESCE(TitleDescription, '')::TEXT AS TitleDescription
    FROM {{ source('stg', 'staging_dim_title') }}
)

SELECT
    TitleCode,
    TitleDescription
FROM cleaned

{% if is_incremental() %}
    WHERE TitleCode NOT IN (SELECT TitleCode FROM {{ this }})
{% endif %}
