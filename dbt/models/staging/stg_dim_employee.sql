-- models/staging/stg_dim_employee.sql
WITH cleaned AS (
    SELECT
        EmployeeID::INT,
        INITCAP(FirstName) AS FirstName,
        INITCAP(LastName) AS LastName,
        COALESCE(LeaveStatusasofJune30, '')::VARCHAR(10) AS LeaveStatusasofJune30
    FROM {{ source('stg', 'staging_dim_employee') }}
)
SELECT * FROM cleaned;
