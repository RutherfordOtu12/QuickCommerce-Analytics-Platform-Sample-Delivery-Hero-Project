"""
QuickShop Analytics - Database Loader
Loads CSV data into SQLite database
"""

import sqlite3
import pandas as pd
import os

# Configuration
DB_PATH = 'quickshop.db'
SCHEMA_PATH = 'schema.sql'
DATA_DIR = '../data'

print("QuickShop Analytics - Database Loader")
print("=" * 60)

# Remove existing database if it exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"Removed existing database: {DB_PATH}")

# Create database connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
print(f"\nCreated new database: {DB_PATH}")

# Execute schema
print("\nExecuting schema...")
with open(SCHEMA_PATH, 'r') as f:
    schema_sql = f.read()
    cursor.executescript(schema_sql)
print("Schema created successfully")

# Load data from CSV files
tables = {
    'local_shops': 'local_shops.csv',
    'products': 'products.csv',
    'customers': 'customers.csv',
    'orders': 'orders.csv',
    'order_items': 'order_items.csv',
    'deliveries': 'deliveries.csv',
    'inventory': 'inventory.csv',
    'promotions': 'promotions.csv'
}

print("\nLoading data into tables...")
for table_name, csv_file in tables.items():
    csv_path = os.path.join(DATA_DIR, csv_file)
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists='append', index=False)
    print(f"  ✓ Loaded {len(df):,} rows into {table_name}")

# Verify data
print("\nVerifying database...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables_in_db = cursor.fetchall()
print(f"  Tables created: {len(tables_in_db)}")

cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
views_in_db = cursor.fetchall()
print(f"  Views created: {len(views_in_db)}")

cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
indexes_in_db = cursor.fetchall()
print(f"  Indexes created: {len(indexes_in_db)}")

# Display sample statistics
print("\n" + "=" * 60)
print("Database Statistics")
print("=" * 60)

stats_queries = [
    ("Total Orders", "SELECT COUNT(*) FROM orders"),
    ("Total Customers", "SELECT COUNT(*) FROM customers"),
    ("Total Products", "SELECT COUNT(*) FROM products"),
    ("Active Shops", "SELECT COUNT(*) FROM local_shops WHERE is_active = 1"),
    ("Total GMV (Delivered)", "SELECT ROUND(SUM(total_amount), 2) FROM orders WHERE status = 'Delivered'"),
    ("Average Order Value", "SELECT ROUND(AVG(total_amount), 2) FROM orders WHERE status = 'Delivered'"),
    ("Order Completion Rate (%)", "SELECT ROUND(CAST(SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) FROM orders"),
]

for stat_name, query in stats_queries:
    cursor.execute(query)
    result = cursor.fetchone()[0]
    print(f"  {stat_name}: {result:,}" if isinstance(result, int) else f"  {stat_name}: {result}")

# Commit and close
conn.commit()
conn.close()

print("\n" + "=" * 60)
print("Database created and loaded successfully!")
print(f"Database location: {DB_PATH}")
print("=" * 60)
