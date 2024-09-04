-- Insert data into the dim_date table on Redshift

INSERT INTO "edw"."dim_date" (DateID, Date, Year, Month, Day, FiscalYear, Quarter, MonthName, DayOfWeek)
WITH DateRange AS (
    SELECT 
        ROW_NUMBER() OVER () - 1 AS RowNum, 
        dateadd(day, ROW_NUMBER() OVER () - 1, '1995-01-01'::date) AS Date
    FROM svv_tables -- Use a system table to ensure we generate a sufficient number of rows
    LIMIT 10500 -- Generate dates for approximately 30 years
),
Populated AS (
    SELECT 
        RowNum + 1 AS DateID, -- Ensures DateID starts from 1
        Date,
        EXTRACT(YEAR FROM Date) AS Year,
        EXTRACT(MONTH FROM Date) AS Month,
        EXTRACT(DAY FROM Date) AS Day,
        CASE 
            WHEN EXTRACT(MONTH FROM Date) IN (1, 2, 3) THEN EXTRACT(YEAR FROM Date) - 1
            ELSE EXTRACT(YEAR FROM Date)
        END AS FiscalYear,
        EXTRACT(QUARTER FROM Date) AS Quarter,
        TO_CHAR(Date, 'Mon') AS MonthName, -- Abbreviated month name
        TO_CHAR(Date, 'Day') AS DayOfWeek -- Full day of the week name
    FROM DateRange
)

SELECT * FROM Populated;