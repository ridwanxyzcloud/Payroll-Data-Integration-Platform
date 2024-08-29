-- models/warehouse/dim_employee.sql
{{ config(
    materialized='incremental',
    unique_key='EmployeeID',
    incremental_strategy='merge'
) }}

with source_data as (
    select distinct
        cast(EmployeeID as int) as EmployeeID,
        cast(FirstName as varchar(50)) as FirstName,
        cast(LastName as varchar(50)) as LastName,
        cast(LeaveStatusasofJune30 as varchar(10)) as LeaveStatusasofJune30
    from {{ ref('stg_dim_employee') }}
)

select
    EmployeeID,
    FirstName,
    LastName,
    LeaveStatusasofJune30
from source_data

{% if is_incremental() %}
    where EmployeeID not in (select EmployeeID from {{ this }})
{% endif %}
