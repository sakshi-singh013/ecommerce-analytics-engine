import os
import duckdb
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "warehouse.duckdb")

def generate_executive_insights():
    con = duckdb.connect(DB_PATH, read_only=True)
    
    # 1. Total Financials
    financials = con.execute("""
        SELECT 
            SUM(net_revenue) AS total_revenue,
            SUM(net_profit) AS total_profit,
            COUNT(order_id) AS total_orders,
            AVG(net_revenue) AS avg_order_value
        FROM main.fct_orders
        WHERE is_successful = true
    """).df().iloc[0]
    
    # 2. Churn Risk Summary
    churn = con.execute("""
        SELECT 
            COUNT(CASE WHEN is_churn_risk THEN 1 END) * 100.0 / COUNT(*) AS churn_risk_pct,
            COUNT(CASE WHEN rfm_segment = 'At Risk' THEN 1 END) AS at_risk_count,
            COUNT(CASE WHEN rfm_segment = 'Lost / Churned' THEN 1 END) AS lost_count
        FROM main.dim_customers
    """).df().iloc[0]
    
    # 3. Top Category
    top_category = con.execute("""
        SELECT category, SUM(total_product_revenue) as rev
        FROM main.dim_products
        GROUP BY 1 ORDER BY rev DESC LIMIT 1
    """).df().iloc[0]
    
    con.close()
    
    insights = [
        f"**Financial Performance**: Total net revenue reached **${financials['total_revenue']:,.2f}** with net profit of **${financials['total_profit']:,.2f}** across **{int(financials['total_orders']):,}** orders (Average Order Value: **${financials['avg_order_value']:.2f}**).",
        f"**Customer Retention Alert**: **{churn['churn_risk_pct']:.1f}%** of customer base is flagged at **Churn Risk**. There are **{int(churn['at_risk_count'])}** customers in 'At Risk' status and **{int(churn['lost_count'])}** in 'Lost / Churned'.",
        f"**Top Performing Category**: **{top_category['category']}** generated the highest total revenue (**${top_category['rev']:,.2f}**).",
        f"**Executive Recommendation**: Launch targeted re-engagement email campaigns and win-back discounts for the 'At Risk' customer cohort to prevent churn and increase LTV."
    ]
    
    return insights

def execute_natural_query(user_query: str):
    user_query_lower = user_query.lower()
    con = duckdb.connect(DB_PATH, read_only=True)
    
    try:
        if "customer" in user_query_lower or "churn" in user_query_lower:
            sql = "SELECT customer_name, email, country, rfm_segment, lifetime_revenue FROM main.dim_customers ORDER BY lifetime_revenue DESC LIMIT 10"
        elif "product" in user_query_lower or "revenue" in user_query_lower:
            sql = "SELECT product_name, category, unit_price, total_units_sold, total_product_revenue FROM main.dim_products ORDER BY total_product_revenue DESC LIMIT 10"
        elif "funnel" in user_query_lower or "conversion" in user_query_lower:
            sql = "SELECT device_type, total_sessions, completed_purchases, conversion_rate_pct FROM main.fct_funnel_events ORDER BY conversion_rate_pct DESC"
        else:
            sql = "SELECT order_id, customer_id, ordered_at, payment_method, net_revenue, net_profit FROM main.fct_orders ORDER BY ordered_at DESC LIMIT 10"
            
        df = con.execute(sql).df()
        con.close()
        return sql, df
    except Exception as e:
        con.close()
        return None, str(e)
