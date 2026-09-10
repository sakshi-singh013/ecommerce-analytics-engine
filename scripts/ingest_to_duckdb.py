import os
import duckdb

# Define Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
DB_PATH = os.path.join(BASE_DIR, "data", "warehouse.duckdb")

print(f"Ingesting raw data into DuckDB warehouse: {DB_PATH}")

# Connect to DuckDB database file (creates it if it doesn't exist)
con = duckdb.connect(DB_PATH)

# Create a dedicated schema for raw staging data
con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

# 1. Ingest Customers CSV
customers_csv = os.path.join(DATA_DIR, "raw_customers.csv").replace("\\", "/")
con.execute(f"""
    CREATE OR REPLACE TABLE raw.customers AS 
    SELECT * FROM read_csv_auto('{customers_csv}');
""")
print("  [OK] Loaded raw.customers")

# 2. Ingest Products CSV
products_csv = os.path.join(DATA_DIR, "raw_products.csv").replace("\\", "/")
con.execute(f"""
    CREATE OR REPLACE TABLE raw.products AS 
    SELECT * FROM read_csv_auto('{products_csv}');
""")
print("  [OK] Loaded raw.products")

# 3. Ingest Orders CSV
orders_csv = os.path.join(DATA_DIR, "raw_orders.csv").replace("\\", "/")
con.execute(f"""
    CREATE OR REPLACE TABLE raw.orders AS 
    SELECT * FROM read_csv_auto('{orders_csv}');
""")
print("  [OK] Loaded raw.orders")

# 4. Ingest Order Items CSV
order_items_csv = os.path.join(DATA_DIR, "raw_order_items.csv").replace("\\", "/")
con.execute(f"""
    CREATE OR REPLACE TABLE raw.order_items AS 
    SELECT * FROM read_csv_auto('{order_items_csv}');
""")
print("  [OK] Loaded raw.order_items")

# 5. Ingest Web Sessions JSON (Using DuckDB's native JSON parser)
web_sessions_json = os.path.join(DATA_DIR, "raw_web_sessions.json").replace("\\", "/")
con.execute(f"""
    CREATE OR REPLACE TABLE raw.web_sessions AS 
    SELECT 
        session_id,
        customer_id,
        device_type,
        CAST(session_start AS TIMESTAMP) AS session_start,
        event_count,
        completed_purchase
    FROM read_json_auto('{web_sessions_json}');
""")
print("  [OK] Loaded raw.web_sessions (parsed from JSON)")

# Print Summary Verification
print("\nDatabase Summary (Row Counts):")
tables = con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'raw';").fetchall()
for (tbl,) in tables:
    count = con.execute(f"SELECT COUNT(*) FROM raw.{tbl}").fetchone()[0]
    print(f"  - raw.{tbl}: {count:,} rows")

con.close()
print("\nRaw Data Ingestion Complete! Your DuckDB Data Warehouse is ready.")
