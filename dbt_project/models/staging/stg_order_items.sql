with source as (
    select * from {{ source('raw', 'order_items') }}
)
select
    order_item_id,
    order_id,
    product_id,
    cast(quantity as integer) as quantity,
    cast(unit_price as decimal(10,2)) as unit_price,
    cast(quantity * unit_price as decimal(10,2)) as gross_item_revenue
from source
