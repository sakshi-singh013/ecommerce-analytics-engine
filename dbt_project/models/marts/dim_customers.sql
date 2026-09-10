with customers as (
    select * from {{ ref('stg_customers') }}
),
orders as (
    select * from {{ ref('fct_orders') }} where is_successful = true
),
customer_orders as (
    select
        customer_id,
        min(ordered_at) as first_order_at,
        max(ordered_at) as last_order_at,
        count(order_id) as total_orders,
        sum(net_revenue) as lifetime_revenue,
        avg(net_revenue) as avg_order_value,
        date_diff('day', max(ordered_at), cast('2026-03-01' as timestamp)) as recency_days
    from orders
    group by 1
)

select
    c.customer_id,
    c.customer_name,
    c.email,
    c.country,
    c.signup_at,
    c.acquisition_channel,
    coalesce(co.total_orders, 0) as total_orders,
    coalesce(co.lifetime_revenue, 0.00) as lifetime_revenue,
    round(coalesce(co.avg_order_value, 0.00), 2) as avg_order_value,
    co.first_order_at,
    co.last_order_at,
    co.recency_days,
    case 
        when co.recency_days <= 30 and co.total_orders >= 5 then 'Champions'
        when co.recency_days <= 60 and co.total_orders >= 3 then 'Loyal Customers'
        when co.recency_days <= 90 then 'Active / Recent'
        when co.recency_days > 90 and co.recency_days <= 180 then 'At Risk'
        when co.recency_days > 180 then 'Lost / Churned'
        else 'Prospect (No Purchase)'
    end as rfm_segment,
    case when co.recency_days > 120 or co.recency_days is null then true else false end as is_churn_risk
from customers c
left join customer_orders co on c.customer_id = co.customer_id
