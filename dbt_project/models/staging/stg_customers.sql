with source as (
    select * from {{ source('raw', 'customers') }}
)
select
    customer_id,
    trim(full_name) as customer_name,
    lower(trim(email)) as email,
    country,
    cast(signup_timestamp as timestamp) as signup_at,
    acquisition_channel
from source
