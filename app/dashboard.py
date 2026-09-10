import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "warehouse.duckdb")

# Add app folder to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_agent import generate_executive_insights, execute_natural_query

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="E-Commerce Analytics & AI Insights Engine",
    page_icon="📊",
    layout="wide"
)

st.title("⚡ E-Commerce Executive Analytics & AI Engine")
st.markdown("*Full-Stack Analytics Platform powered by **DuckDB**, **dbt**, and **AI Automated Insights***")
st.divider()

# Function to load data from DuckDB
@st.cache_data(ttl=60)
def load_data():
    con = duckdb.connect(DB_PATH, read_only=True)
    df_orders = con.execute("SELECT * FROM main.fct_orders").df()
    df_customers = con.execute("SELECT * FROM main.dim_customers").df()
    df_products = con.execute("SELECT * FROM main.dim_products").df()
    df_funnel = con.execute("SELECT * FROM main.fct_funnel_events").df()
    con.close()
    return df_orders, df_customers, df_products, df_funnel

try:
    df_orders, df_customers, df_products, df_funnel = load_data()
except Exception as e:
    st.error(f"Error connecting to DuckDB warehouse at {DB_PATH}: {e}")
    st.stop()

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("🔍 Global Filters")
selected_channel = st.sidebar.multiselect(
    "Acquisition Channel",
    options=df_customers["acquisition_channel"].unique(),
    default=df_customers["acquisition_channel"].unique()
)

selected_category = st.sidebar.multiselect(
    "Product Category",
    options=df_products["category"].unique(),
    default=df_products["category"].unique()
)

# Apply Filters
filtered_customers = df_customers[df_customers["acquisition_channel"].isin(selected_channel)]
filtered_orders = df_orders[df_orders["customer_id"].isin(filtered_customers["customer_id"])]
filtered_products = df_products[df_products["category"].isin(selected_category)]

# ---------------------------------------------------------
# EXECUTIVE KPI METRIC CARDS
# ---------------------------------------------------------
successful_orders = filtered_orders[filtered_orders["is_successful"] == True]

total_revenue = successful_orders["net_revenue"].sum()
total_profit = successful_orders["net_profit"].sum()
total_orders_cnt = len(successful_orders)
aov = successful_orders["net_revenue"].mean() if total_orders_cnt > 0 else 0
churn_pct = (filtered_customers["is_churn_risk"].sum() / len(filtered_customers) * 100) if len(filtered_customers) > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Net Revenue", f"${total_revenue:,.2f}")
col2.metric("Net Profit", f"${total_profit:,.2f}")
col3.metric("Successful Orders", f"{total_orders_cnt:,}")
col4.metric("Avg Order Value (AOV)", f"${aov:.2f}")
col5.metric("Churn Risk Rate", f"{churn_pct:.1f}%", delta="-High Risk" if churn_pct > 25 else "Normal", delta_color="inverse")

st.divider()

# ---------------------------------------------------------
# MAIN DASHBOARD TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Revenue & Financials", 
    "👥 Customer RFM & Churn", 
    "📦 Product Performance", 
    "🤖 AI Executive Insights"
])

# TAB 1: REVENUE & FINANCIALS
with tab1:
    st.subheader("Monthly Revenue & Net Profit Trend")
    filtered_orders['ordered_at'] = pd.to_datetime(filtered_orders['ordered_at'])
    monthly_df = filtered_orders[filtered_orders['is_successful'] == True].set_index('ordered_at').resample('M')[['net_revenue', 'net_profit']].sum().reset_index()
    monthly_df['ordered_at'] = monthly_df['ordered_at'].dt.strftime('%Y-%b')
    
    fig_rev = px.bar(
        monthly_df, 
        x='ordered_at', 
        y=['net_revenue', 'net_profit'],
        barmode='group',
        labels={'value': 'Amount ($)', 'ordered_at': 'Month', 'variable': 'Metric'},
        title="Monthly Net Revenue vs Net Profit",
        color_discrete_map={'net_revenue': '#1f77b4', 'net_profit': '#2ca02c'}
    )
    st.plotly_chart(fig_rev, use_container_width=True)

# TAB 2: CUSTOMER RFM & CHURN
with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Customer RFM Segment Distribution")
        rfm_counts = filtered_customers['rfm_segment'].value_counts().reset_index()
        rfm_counts.columns = ['rfm_segment', 'count']
        fig_rfm = px.pie(
            rfm_counts, 
            names='rfm_segment', 
            values='count',
            hole=0.4,
            title="Customer Base Segmentation"
        )
        st.plotly_chart(fig_rfm, use_container_width=True)
        
    with col_b:
        st.subheader("Device Conversion Rate Funnel")
        fig_funnel = px.bar(
            df_funnel,
            x='device_type',
            y='conversion_rate_pct',
            color='device_type',
            text_auto=True,
            title="Conversion Rate (%) by Device Type"
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

# TAB 3: PRODUCT PERFORMANCE
with tab3:
    st.subheader("Top Products by Net Revenue")
    top_prod = filtered_products.sort_values(by='total_product_revenue', ascending=False).head(10)
    fig_prod = px.bar(
        top_prod,
        x='total_product_revenue',
        y='product_name',
        orientation='h',
        color='category',
        title="Top 10 Revenue Generating Products",
        labels={'total_product_revenue': 'Total Revenue ($)', 'product_name': 'Product Name'}
    )
    st.plotly_chart(fig_prod, use_container_width=True)

# TAB 4: AI EXECUTIVE INSIGHTS & ASK YOUR DATA
with tab4:
    st.subheader("🤖 Automated Executive AI Insights")
    insights = generate_executive_insights()
    for insight in insights:
        st.info(insight)
        
    st.divider()
    st.subheader("💬 Ask Your Data (Natural Language Query)")
    user_prompt = st.text_input(
        "Enter a question about your business (e.g., 'show top products', 'list churned customers', 'show funnel conversion'):",
        placeholder="e.g. show top products by revenue"
    )
    
    if user_prompt:
        sql_used, df_result = execute_natural_query(user_prompt)
        if sql_used:
            st.success(f"**Executed SQL Query:** `{sql_used}`")
            st.dataframe(df_result, use_container_width=True)
        else:
            st.error(df_result)
