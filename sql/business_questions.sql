-- Analyze total payroll and overtime by agency for a given fiscal year
select
    AgencyName,
    FiscalYear,
    TotalBaseSalary,
    TotalRegularGrossPaid,
    TotalOTPaid,
    TotalSupplementalPay,
    (TotalOTPaid / TotalRegularGrossPaid) * 100 as OvertimePercentage
from
    {{ ref('payroll_aggregate_by_agency') }}
where
    FiscalYear = 2023
order by
    OvertimePercentage desc;
