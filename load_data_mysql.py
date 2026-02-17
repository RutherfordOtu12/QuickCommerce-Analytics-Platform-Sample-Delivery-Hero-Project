#!/usr/bin/env python3
"""
QuickShop Analytics Platform - MySQL Data Loader
Loads CSV data into MySQL database
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root', 
    'password': 'Houseofgod12!',
    'database': 'quickshop'
}

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

def create_connection():
    """Create MySQL database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print(f"✓ Connected to MySQL database: {DB_CONFIG['database']}")
            return connection
    except Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        return None

def load_csv_to_table(connection, csv_file, table_name, chunk_size=1000):
    """Load CSV file into MySQL table"""
    try:
        print(f"\nLoading {csv_file} into {table_name}...")
        
        # Read CSV
        df = pd.read_csv(DATA_DIR / csv_file)
        
        # Replace NaN with None (NULL in MySQL)
        df = df.where(pd.notnull(df), None)
        
        print(f"  Read {len(df)} rows from CSV")
        
        # Get cursor
        cursor = connection.cursor()
        
        # Prepare INSERT statement
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # Insert data in chunks
        total_inserted = 0
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            data = [tuple(row) for row in chunk.values]
            cursor.executemany(insert_query, data)
            connection.commit()
            total_inserted += len(chunk)
            print(f"  Inserted {total_inserted}/{len(df)} rows...", end='\r')
        
        print(f"\n  ✓ Successfully loaded {total_inserted} rows into {table_name}")
        cursor.close()
        return True
        
    except Error as e:
        print(f"  ✗ Error loading {csv_file}: {e}")
        connection.rollback()
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        connection.rollback()
        return False

def verify_data(connection):
    """Verify loaded data with sample queries"""
    try:
        cursor = connection.cursor()
        
        print("\n" + "="*60)
        print("DATA VERIFICATION")
        print("="*60)
        
        # Count rows in each table
        tables = ['customers', 'local_shops', 'products', 'orders', 
                  'order_items', 'deliveries', 'inventory', 'promotions']
        
        print("\nTable Row Counts:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:20s}: {count:>8,} rows")
        
        # Sample business metrics
        print("\nBusiness Metrics:")
        
        # Total GMV
        cursor.execute("""
            SELECT SUM(total_amount) as total_gmv
            FROM orders
            WHERE status = 'Delivered'
        """)
        gmv = cursor.fetchone()[0]
        print(f"  Total GMV: €{gmv:,.2f}")
        
        # Total orders
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Delivered'")
        orders = cursor.fetchone()[0]
        print(f"  Delivered Orders: {orders:,}")
        
        # Average order value
        cursor.execute("""
            SELECT AVG(total_amount) as aov
            FROM orders
            WHERE status = 'Delivered'
        """)
        aov = cursor.fetchone()[0]
        print(f"  Average Order Value: €{aov:.2f}")
        
        # Completion rate
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'Delivered' THEN 1 END) * 100.0 / COUNT(*) as completion_rate
            FROM orders
        """)
        completion = cursor.fetchone()[0]
        print(f"  Order Completion Rate: {completion:.1f}%")
        
        # Active customers (skip if column doesn't exist)
        try:
            cursor.execute("SELECT COUNT(*) FROM customers WHERE total_orders > 0")
            active_customers = cursor.fetchone()[0]
            print(f"  Active Customers: {active_customers:,}")
        except:
            pass
        
        # Active shops
        cursor.execute("SELECT COUNT(*) FROM local_shops WHERE is_active = 1")
        active_shops = cursor.fetchone()[0]
        print(f"  Active Shops: {active_shops:,}")
        
        # Date range
        cursor.execute("""
            SELECT 
                MIN(DATE(order_date)) as first_order,
                MAX(DATE(order_date)) as last_order
            FROM orders
        """)
        first_date, last_date = cursor.fetchone()
        print(f"  Date Range: {first_date} to {last_date}")
        
        print("\n✓ Data verification complete!")
        cursor.close()
        
    except Error as e:
        print(f"\n✗ Error during verification: {e}")

def main():
    """Main execution function"""
    print("="*60)
    print("QuickShop Analytics - MySQL Data Loader")
    print("="*60)
    
    # Check if CSV files exist
    required_files = [
        'customers.csv',
        'local_shops.csv',
        'products.csv',
        'orders.csv',
        'order_items.csv',
        'deliveries.csv',
        'inventory.csv',
        'promotions.csv'
    ]
    
    print("\nChecking for required CSV files...")
    missing_files = []
    for file in required_files:
        if not (DATA_DIR / file).exists():
            missing_files.append(file)
            print(f"  ✗ Missing: {file}")
        else:
            print(f"  ✓ Found: {file}")
    
    if missing_files:
        print(f"\n✗ Error: {len(missing_files)} required file(s) missing!")
        print("  Run generate_dataset.py first to create the data.")
        return
    
    # Create database connection
    print("\nConnecting to MySQL...")
    connection = create_connection()
    
    if not connection:
        print("\n✗ Failed to connect to MySQL database!")
        print("\nTroubleshooting:")
        print("  1. Make sure MySQL is running")
        print("  2. Update DB_CONFIG in this script with your credentials")
        print("  3. Create the database first: CREATE DATABASE quickshop;")
        print("  4. Run the schema: mysql -u root -p quickshop < schema_mysql.sql")
        return
    
    try:
        # Load data in order (respecting foreign key constraints)
        load_order = [
            ('customers.csv', 'customers'),
            ('local_shops.csv', 'local_shops'),
            ('products.csv', 'products'),
            ('orders.csv', 'orders'),
            ('order_items.csv', 'order_items'),
            ('deliveries.csv', 'deliveries'),
            ('inventory.csv', 'inventory'),
            ('promotions.csv', 'promotions')
        ]
        
        print("\n" + "="*60)
        print("LOADING DATA")
        print("="*60)
        
        success_count = 0
        for csv_file, table_name in load_order:
            if load_csv_to_table(connection, csv_file, table_name):
                success_count += 1
        
        print(f"\n✓ Successfully loaded {success_count}/{len(load_order)} tables")
        
        # Verify data
        verify_data(connection)
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Connect Tableau to MySQL:")
        print(f"   Host: {DB_CONFIG['host']}")
        print(f"   Port: {DB_CONFIG['port']}")
        print(f"   Database: {DB_CONFIG['database']}")
        print(f"   Username: {DB_CONFIG['user']}")
        print("\n2. Run SQL queries:")
        print("   mysql -u root -p quickshop < sql_queries/analytics_queries.sql")
        print("\n3. Test views:")
        print("   SELECT * FROM daily_metrics LIMIT 10;")
        print("\n4. Build Tableau dashboards using TABLEAU_DASHBOARD_GUIDE.md")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n✓ MySQL connection closed")

if __name__ == "__main__":
    main()
