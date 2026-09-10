with source as (
    select * from {{ source('raw', 'orders') }}
)
select
    order_id,
    customer_id,
    cast(order_timestamp as timestamp) as ordered_at,
    payment_method,
    order_status,
    cast(shipping_cost as decimal(10,2)) as shipping_cost,
    cast(discount_amount as decimal(10,2)) as discount_amount,
    case when order_status = 'Completed' then true else false end as is_successful
from source
