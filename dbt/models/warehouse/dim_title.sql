-- models/warehouse/dim_title.sql
{{ config(
    materialized='incremental',
    unique_key='TitleCode',
    incremental_strategy='merge'
) }}

with source_data as (
    select distinct
        cast(TitleCode as int) as TitleCode,
        cast(TitleDescription as text) as TitleDescription
    from {{ ref('stg_dim_title') }}
)

select
    TitleCode,
    TitleDescription
from source_data

{% if is_incremental() %}
    where TitleCode not in (select TitleCode from {{ this }})
{% endif %}
