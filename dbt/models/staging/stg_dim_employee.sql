-- models/staging/stg_dim_employee.sql
select
    EmployeeID,
    FirstName,
    LastName,
    LeaveStatusasofJune30
from {{ source('stg', 'staging_dim_employee') }}
