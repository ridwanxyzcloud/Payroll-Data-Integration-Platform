-- models/warehouse/dim_agency.sql
{{ config(
    materialized='incremental',
    unique_key='AgencyID',
    incremental_strategy='merge'
) }}

with source_data as (
    select distinct
        cast(AgencyID as int) as AgencyID,
        cast(AgencyName as varchar(100)) as AgencyName,
        cast(AgencyStartDate as date) as AgencyStartDate
    from {{ ref('stg_dim_agency') }}
)

select
    AgencyID,
    AgencyName,
    AgencyStartDate
from source_data

{% if is_incremental() %}
    where AgencyID not in (select AgencyID from {{ this }})
{% endif %}
