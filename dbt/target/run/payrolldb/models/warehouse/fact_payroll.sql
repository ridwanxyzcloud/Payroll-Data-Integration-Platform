
      -- back compat for old kwarg name
  
  
        
            
            
        
    

    

    merge into "payrolldb"."edw_edw"."fact_payroll"
        using "fact_payroll__dbt_tmp192616171250" as DBT_INTERNAL_SOURCE
        on (
                DBT_INTERNAL_SOURCE.PayrollID = "payrolldb"."edw_edw"."fact_payroll".PayrollID
            )

    
    when matched then update set
        "payrollid" = DBT_INTERNAL_SOURCE."payrollid", 
        "payrollnumber" = DBT_INTERNAL_SOURCE."payrollnumber", 
        "employeeid" = DBT_INTERNAL_SOURCE."employeeid", 
        "agencyid" = DBT_INTERNAL_SOURCE."agencyid", 
        "titlecode" = DBT_INTERNAL_SOURCE."titlecode", 
        "dateid" = DBT_INTERNAL_SOURCE."dateid", 
        "basesalary" = DBT_INTERNAL_SOURCE."basesalary", 
        "regularhours" = DBT_INTERNAL_SOURCE."regularhours", 
        "regulargrosspaid" = DBT_INTERNAL_SOURCE."regulargrosspaid", 
        "othours" = DBT_INTERNAL_SOURCE."othours", 
        "totalotpaid" = DBT_INTERNAL_SOURCE."totalotpaid", 
        "totalotherpay" = DBT_INTERNAL_SOURCE."totalotherpay", 
        "worklocationborough" = DBT_INTERNAL_SOURCE."worklocationborough"
        
    

    when not matched then insert (
        "payrollid", 
        "payrollnumber", 
        "employeeid", 
        "agencyid", 
        "titlecode", 
        "dateid", 
        "basesalary", 
        "regularhours", 
        "regulargrosspaid", 
        "othours", 
        "totalotpaid", 
        "totalotherpay", 
        "worklocationborough"
        
    )
    values (
        DBT_INTERNAL_SOURCE."payrollid", 
        DBT_INTERNAL_SOURCE."payrollnumber", 
        DBT_INTERNAL_SOURCE."employeeid", 
        DBT_INTERNAL_SOURCE."agencyid", 
        DBT_INTERNAL_SOURCE."titlecode", 
        DBT_INTERNAL_SOURCE."dateid", 
        DBT_INTERNAL_SOURCE."basesalary", 
        DBT_INTERNAL_SOURCE."regularhours", 
        DBT_INTERNAL_SOURCE."regulargrosspaid", 
        DBT_INTERNAL_SOURCE."othours", 
        DBT_INTERNAL_SOURCE."totalotpaid", 
        DBT_INTERNAL_SOURCE."totalotherpay", 
        DBT_INTERNAL_SOURCE."worklocationborough"
        
    )


  