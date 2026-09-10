# 📊 Autonomous E-Commerce Analytics & AI Executive Insights Engine

> An end-to-end Modern Data Stack (MDS) platform built with **DuckDB**, **dbt**, **Streamlit**, and **AI Automated Insights**.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![dbt](https://img.shields.io/badge/dbt--core-1.10.23-orange.svg)
![DuckDB](https://img.shields.io/badge/DuckDB-Latest-yellow.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.42+-red.svg)

---

## 🎯 Architecture & Data Flow

```
[ Raw Event Logs (CSV/JSON) ] 
            │
            ▼  (ingest_to_duckdb.py)
   [ DuckDB Warehouse ]  ── (raw schema)
            │
            ▼  (dbt run & dbt test)
   [ Dimensional Models ] ── (Staging & Marts Star Schema)
            │
            ▼  (Streamlit & AI Agent)
[ Interactive BI Dashboard & AI Executive Insights ]
```

---

## 🚀 Key Features

1. **High-Performance Ingestion**: Ingests raw clickstream sessions (JSON) and orders/customers (CSV) into a local **DuckDB** analytical engine.
2. **Analytics Engineering with dbt**:
   - **Staging Layer**: Normalization, data type casting, and schema validation.
   - **Marts Layer**: Star Schema modeling containing `dim_customers` (RFM Cohorts & Churn Risk), `dim_products` (Margin & Velocity), `fct_orders` (Net Revenue & Profit), and `fct_funnel_events` (Device Conversion).
3. **Data Quality Governance**: Enforces 10 data quality tests (`dbt test`) covering `unique` and `not_null` primary/foreign keys.
4. **Executive Dashboard**: Interactive **Streamlit** dashboard built with **Plotly** visualizations.
5. **AI Automated Insights**: Rule-based & LLM agent generating real-time executive summaries and plain-English data querying.

---

## 🛠️ Quickstart Instructions

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ecommerce-analytics-engine.git
cd ecommerce-analytics-engine

# 2. Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install pandas faker duckdb dbt-core dbt-duckdb streamlit plotly polars

# 4. Generate raw synthetic datasets
python scripts/generate_raw_data.py

# 5. Ingest into DuckDB warehouse
python scripts/ingest_to_duckdb.py

# 6. Run dbt models and data tests
cd dbt_project
dbt run --profiles-dir .
dbt test --profiles-dir .

# 7. Launch Streamlit Dashboard
cd ..
streamlit run app/dashboard.py
```
