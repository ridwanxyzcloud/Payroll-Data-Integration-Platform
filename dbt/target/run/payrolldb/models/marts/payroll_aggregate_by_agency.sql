
      -- back compat for old kwarg name
  
  
        
            
            
        
    

    

    merge into "payrolldb"."edw_marts"."payroll_aggregate_by_agency"
        using "payroll_aggregate_by_agency__dbt_tmp114144436713" as DBT_INTERNAL_SOURCE
        on (
                DBT_INTERNAL_SOURCE.(AgencyID, FiscalYear) = "payrolldb"."edw_marts"."payroll_aggregate_by_agency".(AgencyID, FiscalYear)
            )

    
    when matched then update set
        "agencyid" = DBT_INTERNAL_SOURCE."agencyid", 
        "agencyname" = DBT_INTERNAL_SOURCE."agencyname", 
        "fiscalyear" = DBT_INTERNAL_SOURCE."fiscalyear", 
        "totalbasesalary" = DBT_INTERNAL_SOURCE."totalbasesalary", 
        "totalregulargrosspaid" = DBT_INTERNAL_SOURCE."totalregulargrosspaid", 
        "totalothours" = DBT_INTERNAL_SOURCE."totalothours", 
        "totalotpaid" = DBT_INTERNAL_SOURCE."totalotpaid", 
        "totalotherpay" = DBT_INTERNAL_SOURCE."totalotherpay", 
        "totalsupplementalpay" = DBT_INTERNAL_SOURCE."totalsupplementalpay", 
        "totalemployees" = DBT_INTERNAL_SOURCE."totalemployees"
        
    

    when not matched then insert (
        "agencyid", 
        "agencyname", 
        "fiscalyear", 
        "totalbasesalary", 
        "totalregulargrosspaid", 
        "totalothours", 
        "totalotpaid", 
        "totalotherpay", 
        "totalsupplementalpay", 
        "totalemployees"
        
    )
    values (
        DBT_INTERNAL_SOURCE."agencyid", 
        DBT_INTERNAL_SOURCE."agencyname", 
        DBT_INTERNAL_SOURCE."fiscalyear", 
        DBT_INTERNAL_SOURCE."totalbasesalary", 
        DBT_INTERNAL_SOURCE."totalregulargrosspaid", 
        DBT_INTERNAL_SOURCE."totalothours", 
        DBT_INTERNAL_SOURCE."totalotpaid", 
        DBT_INTERNAL_SOURCE."totalotherpay", 
        DBT_INTERNAL_SOURCE."totalsupplementalpay", 
        DBT_INTERNAL_SOURCE."totalemployees"
        
    )


  