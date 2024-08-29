-- models/warehouse/dim_date.sql
{{ config(
    materialized='table'
) }}

WITH DateRange AS (
    SELECT generate_series(
        '1990-01-01'::date, 
        '2030-12-31'::date, 
        '1 day'::interval
    ) AS Date
)

, populated AS (
    SELECT 
        ROW_NUMBER() OVER () AS DateID,
        Date,
        EXTRACT(YEAR FROM Date) AS Year,
        EXTRACT(MONTH FROM Date) AS Month,
        EXTRACT(DAY FROM Date) AS Day,
        CASE 
            WHEN EXTRACT(MONTH FROM Date) IN (1, 2, 3) THEN EXTRACT(YEAR FROM Date) - 1
            ELSE EXTRACT(YEAR FROM Date)
        END AS FiscalYear,
        EXTRACT(QUARTER FROM Date) AS Quarter,
        TO_CHAR(Date, 'Month') AS MonthName,
        TO_CHAR(Date, 'Day') AS DayOfWeek
    FROM DateRange
)

SELECT * FROM populated;
