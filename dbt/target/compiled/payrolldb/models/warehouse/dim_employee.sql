-- models/warehouse/dim_employee.sql

WITH cleaned AS (
    SELECT
        -- Initial cleaning and transformation
        DISTINCT
        EmployeeID::INT AS EmployeeID,
        INITCAP(FirstName) AS FirstName,
        INITCAP(LastName) AS LastName,
        COALESCE(LeaveStatusasofJune30, '')::VARCHAR(10) AS LeaveStatusasofJune30
    FROM "payrolldb"."stg"."staging_dim_employee"
)

SELECT
    EmployeeID,
    FirstName,
    LastName,
    LeaveStatusasofJune30
FROM cleaned


    WHERE EmployeeID NOT IN (SELECT EmployeeID FROM "payrolldb"."edw_edw"."dim_employee")
