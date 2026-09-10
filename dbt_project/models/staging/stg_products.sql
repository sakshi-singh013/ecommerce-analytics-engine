with source as (
    select * from {{ source('raw', 'products') }}
)
select
    product_id,
    trim(product_name) as product_name,
    category,
    cast(price as decimal(10,2)) as unit_price,
    cast(cost_price as decimal(10,2)) as unit_cost,
    cast(price - cost_price as decimal(10,2)) as profit_margin_amount,
    round(cast((price - cost_price) / price * 100 as decimal(10,2)), 2) as profit_margin_pct,
    stock_level
from source
