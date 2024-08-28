-- models/warehouse/fact_payroll.sql
{{ config(
    materialized='incremental',
    unique_key='PayrollID',
    incremental_strategy='merge'
) }}

with source_data as (
    select distinct
        {{ dbt_utils.surrogate_key(['EmployeeID', 'AgencyID', 'TitleCode', 'FiscalYear', 'PayrollNumber']) }} as PayrollID,
        cast(EmployeeID as int) as EmployeeID,
        cast(AgencyID as int) as AgencyID,
        cast(TitleCode as int) as TitleCode,
        cast(FiscalYear as int) as FiscalYear,
        cast(PayrollNumber as int) as PayrollNumber,
        cast(BaseSalary as decimal(10,2)) as BaseSalary,
        cast(RegularHours as decimal(10,2)) as RegularHours,
        cast(RegularGrossPaid as decimal(10,2)) as RegularGrossPaid,
        cast(OTHours as decimal(10,2)) as OTHours,
        cast(TotalOTPaid as decimal(10,2)) as TotalOTPaid,
        cast(TotalOtherPay as decimal(10,2)) as TotalOtherPaid,
        cast(WorkLocationBorough as varchar(20)) as WorkLocationBorough
    from {{ ref('stg_fact_payroll') }}
)

select
    PayrollID,
    EmployeeID,
    AgencyID,
    TitleCode,
    FiscalYear,
    PayrollNumber,
    BaseSalary,
    RegularHours,
    RegularGrossPaid,
    OTHours,
    TotalOTPaid,
    TotalOtherPaid,
    WorkLocationBorough
from source_data

{% if is_incremental() %}
    where PayrollNumber not in (select PayrollNumber from {{ this }})
{% endif %}
