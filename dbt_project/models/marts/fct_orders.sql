with orders as (
    select * from {{ ref('stg_orders') }}
),
order_items as (
    select 
        order_id,
        count(distinct product_id) as total_unique_items,
        sum(quantity) as total_quantity_items,
        sum(gross_item_revenue) as gross_revenue
    from {{ ref('stg_order_items') }}
    group by 1
),
products_cost as (
    select 
        oi.order_id,
        sum(oi.quantity * p.unit_cost) as total_order_cost
    from {{ ref('stg_order_items') }} oi
    join {{ ref('stg_products') }} p on oi.product_id = p.product_id
    group by 1
)

select
    o.order_id,
    o.customer_id,
    o.ordered_at,
    o.payment_method,
    o.order_status,
    o.is_successful,
    coalesce(i.total_unique_items, 0) as total_unique_items,
    coalesce(i.total_quantity_items, 0) as total_quantity_items,
    coalesce(i.gross_revenue, 0) as gross_revenue,
    o.discount_amount,
    o.shipping_cost,
    cast(coalesce(i.gross_revenue, 0) - o.discount_amount + o.shipping_cost as decimal(10,2)) as net_revenue,
    cast(pc.total_order_cost as decimal(10,2)) as total_cost,
    cast((coalesce(i.gross_revenue, 0) - o.discount_amount + o.shipping_cost) - pc.total_order_cost as decimal(10,2)) as net_profit
from orders o
left join order_items i on o.order_id = i.order_id
left join products_cost pc on o.order_id = pc.order_id
