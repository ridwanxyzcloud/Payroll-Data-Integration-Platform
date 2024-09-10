
      -- back compat for old kwarg name
  
  
        
            
            
        
    

    

    merge into "payrolldb"."edw_edw"."dim_title"
        using "dim_title__dbt_tmp192616089339" as DBT_INTERNAL_SOURCE
        on (
                DBT_INTERNAL_SOURCE.TitleCode = "payrolldb"."edw_edw"."dim_title".TitleCode
            )

    
    when matched then update set
        "titlecode" = DBT_INTERNAL_SOURCE."titlecode", 
        "titledescription" = DBT_INTERNAL_SOURCE."titledescription"
        
    

    when not matched then insert (
        "titlecode", 
        "titledescription"
        
    )
    values (
        DBT_INTERNAL_SOURCE."titlecode", 
        DBT_INTERNAL_SOURCE."titledescription"
        
    )


  