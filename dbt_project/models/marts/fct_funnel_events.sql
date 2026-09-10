with sessions as (
    select * from {{ ref('stg_web_sessions') }}
)
select
    device_type,
    count(session_id) as total_sessions,
    count(case when is_purchase_completed then 1 end) as completed_purchases,
    round(cast(count(case when is_purchase_completed then 1 end) as double) / count(session_id) * 100, 2) as conversion_rate_pct
from sessions
group by 1
