-- models/marts/payroll_aggregate_by_agency.sql
{{ config(
    materialized='table'
) }}

with source_data as (
    select
        a.AgencyID,
        a.AgencyName,
        f.FiscalYear,
        sum(f.BaseSalary) as TotalBaseSalary,
        sum(f.RegularGrossPaid) as TotalRegularGrossPaid,
        sum(f.OTHours) as TotalOTHours,
        sum(f.TotalOTPaid) as TotalOTPaid,
        sum(f.TotalOtherPaid) as TotalOtherPaid,
        sum(f.TotalOTPaid + f.TotalOtherPaid) as TotalSupplementalPay,
        count(distinct f.EmployeeID) as TotalEmployees
    from
        {{ ref('fact_payroll') }} f
    join
        {{ ref('dim_agency') }} a
    on
        f.AgencyID = a.AgencyID
    group by
        a.AgencyID, a.AgencyName, f.FiscalYear
)

select
    AgencyID,
    AgencyName,
    FiscalYear,
    TotalBaseSalary,
    TotalRegularGrossPaid,
    TotalOTHours,
    TotalOTPaid,
    TotalOtherPaid,
    TotalSupplementalPay,
    TotalEmployees
from source_data
