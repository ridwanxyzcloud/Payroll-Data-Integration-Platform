-- models/staging/stg_dim_agency.sql
select
    AgencyID,
    AgencyName,
    AgencyStartDate
from {{ source('stg', 'staging_dim_agency') }}
