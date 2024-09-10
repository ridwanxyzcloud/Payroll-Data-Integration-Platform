
      -- back compat for old kwarg name
  
  
        
            
            
        
    

    

    merge into "payrolldb"."edw_edw"."dim_employee"
        using "dim_employee__dbt_tmp192616072739" as DBT_INTERNAL_SOURCE
        on (
                DBT_INTERNAL_SOURCE.EmployeeID = "payrolldb"."edw_edw"."dim_employee".EmployeeID
            )

    
    when matched then update set
        "employeeid" = DBT_INTERNAL_SOURCE."employeeid", 
        "firstname" = DBT_INTERNAL_SOURCE."firstname", 
        "lastname" = DBT_INTERNAL_SOURCE."lastname", 
        "leavestatusasofjune30" = DBT_INTERNAL_SOURCE."leavestatusasofjune30"
        
    

    when not matched then insert (
        "employeeid", 
        "firstname", 
        "lastname", 
        "leavestatusasofjune30"
        
    )
    values (
        DBT_INTERNAL_SOURCE."employeeid", 
        DBT_INTERNAL_SOURCE."firstname", 
        DBT_INTERNAL_SOURCE."lastname", 
        DBT_INTERNAL_SOURCE."leavestatusasofjune30"
        
    )


  