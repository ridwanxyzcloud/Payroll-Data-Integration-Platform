-- models/warehouse/dim_title.sql

WITH cleaned AS (
    SELECT DISTINCT
        TitleCode::INT AS TitleCode,
        COALESCE(TitleDescription, '')::TEXT AS TitleDescription
    FROM "payrolldb"."stg"."staging_dim_title"
)

SELECT
    TitleCode,
    TitleDescription
FROM cleaned


    WHERE TitleCode NOT IN (SELECT TitleCode FROM "payrolldb"."edw_edw"."dim_title")
