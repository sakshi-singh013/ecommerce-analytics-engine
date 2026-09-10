with source as (
    select * from {{ source('raw', 'web_sessions') }}
)
select
    session_id,
    customer_id,
    device_type,
    cast(session_start as timestamp) as session_start_at,
    event_count,
    completed_purchase as is_purchase_completed
from source
