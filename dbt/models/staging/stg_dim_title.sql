-- models/staging/stg_dim_title.sql
select
    TitleCode,
    TitleDescription
from {{ source('stg', 'staging_dim_title') }}
