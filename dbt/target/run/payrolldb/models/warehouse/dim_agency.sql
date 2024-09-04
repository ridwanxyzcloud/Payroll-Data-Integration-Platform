
      -- back compat for old kwarg name
  
  
        
            
            
        
    

    

    merge into "payrolldb"."edw_edw"."dim_agency"
        using "dim_agency__dbt_tmp114139825523" as DBT_INTERNAL_SOURCE
        on (
                DBT_INTERNAL_SOURCE.AgencyID = "payrolldb"."edw_edw"."dim_agency".AgencyID
            )

    
    when matched then update set
        "agencyid" = DBT_INTERNAL_SOURCE."agencyid", 
        "agencyname" = DBT_INTERNAL_SOURCE."agencyname", 
        "agencystartdate" = DBT_INTERNAL_SOURCE."agencystartdate"
        
    

    when not matched then insert (
        "agencyid", 
        "agencyname", 
        "agencystartdate"
        
    )
    values (
        DBT_INTERNAL_SOURCE."agencyid", 
        DBT_INTERNAL_SOURCE."agencyname", 
        DBT_INTERNAL_SOURCE."agencystartdate"
        
    )


  