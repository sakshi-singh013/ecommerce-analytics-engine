with products as (
    select * from {{ ref('stg_products') }}
),
order_items as (
    select 
        product_id,
        sum(quantity) as total_units_sold,
        sum(gross_item_revenue) as total_product_revenue
    from {{ ref('stg_order_items') }} oi
    join {{ ref('stg_orders') }} o on oi.order_id = o.order_id
    where o.is_successful = true
    group by 1
)

select
    p.product_id,
    p.product_name,
    p.category,
    p.unit_price,
    p.unit_cost,
    p.profit_margin_amount,
    p.profit_margin_pct,
    p.stock_level,
    coalesce(oi.total_units_sold, 0) as total_units_sold,
    coalesce(oi.total_product_revenue, 0.00) as total_product_revenue
from products p
left join order_items oi on p.product_id = oi.product_id
