
      -- back compat for old kwarg name
  
  
        
            
            
        
    

    

    merge into "payrolldb"."edw_marts"."overtime_by_employee_and_agency"
        using "overtime_by_employee_and_agency__dbt_tmp192620543092" as DBT_INTERNAL_SOURCE
        on (
                DBT_INTERNAL_SOURCE.(EmployeeID, AgencyID) = "payrolldb"."edw_marts"."overtime_by_employee_and_agency".(EmployeeID, AgencyID)
            )

    
    when matched then update set
        "employeeid" = DBT_INTERNAL_SOURCE."employeeid", 
        "firstname" = DBT_INTERNAL_SOURCE."firstname", 
        "lastname" = DBT_INTERNAL_SOURCE."lastname", 
        "agencyid" = DBT_INTERNAL_SOURCE."agencyid", 
        "agencyname" = DBT_INTERNAL_SOURCE."agencyname", 
        "totalothours" = DBT_INTERNAL_SOURCE."totalothours", 
        "totalotpaid" = DBT_INTERNAL_SOURCE."totalotpaid"
        
    

    when not matched then insert (
        "employeeid", 
        "firstname", 
        "lastname", 
        "agencyid", 
        "agencyname", 
        "totalothours", 
        "totalotpaid"
        
    )
    values (
        DBT_INTERNAL_SOURCE."employeeid", 
        DBT_INTERNAL_SOURCE."firstname", 
        DBT_INTERNAL_SOURCE."lastname", 
        DBT_INTERNAL_SOURCE."agencyid", 
        DBT_INTERNAL_SOURCE."agencyname", 
        DBT_INTERNAL_SOURCE."totalothours", 
        DBT_INTERNAL_SOURCE."totalotpaid"
        
    )


  