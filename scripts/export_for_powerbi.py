import os
import duckdb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "warehouse.duckdb")
EXPORT_DIR = os.path.join(BASE_DIR, "data", "export")

os.makedirs(EXPORT_DIR, exist_ok=True)

print(f"Exporting clean dbt mart tables for Power BI from: {DB_PATH}")

con = duckdb.connect(DB_PATH, read_only=True)

marts = ['fct_orders', 'dim_customers', 'dim_products', 'fct_funnel_events']

for table in marts:
    csv_file = os.path.join(EXPORT_DIR, f"{table}.csv").replace("\\", "/")
    con.execute(f"COPY main.{table} TO '{csv_file}' (HEADER, DELIMITER ',');")
    print(f"  [OK] Exported main.{table} -> {csv_file}")

con.close()
print("\nExport Complete! Files ready for Power BI in: data/export/")
