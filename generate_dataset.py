"""
QuickShop Analytics - Realistic Dataset Generator
Generates synthetic but realistic data for a quick commerce platform
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 2, 13)
NUM_CUSTOMERS = 5000
NUM_LOCAL_SHOPS = 150
NUM_PRODUCTS = 500
NUM_ORDERS = 25000

# Helper functions
def random_date(start, end):
    """Generate random datetime between start and end"""
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86400)
    return start + timedelta(days=random_days, seconds=random_seconds)

def weighted_choice(choices, weights):
    """Make weighted random choice"""
    return random.choices(choices, weights=weights, k=1)[0]

print("Generating QuickShop Analytics Dataset...")
print("=" * 60)

# 1. Generate Local Shops
print("\n1. Generating local_shops table...")
shop_types = ['Supermarket', 'Grocery Store', 'Specialty Store', 'Butcher', 
              'Bakery', 'Wine Merchant', 'Greengrocer', 'Convenience Store']
cities = ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne', 'Stuttgart', 
          'Düsseldorf', 'Dortmund', 'Leipzig', 'Dresden']
districts = ['Mitte', 'Kreuzberg', 'Prenzlauer Berg', 'Charlottenburg', 'Neukölln',
             'Friedrichshain', 'Schöneberg', 'Tempelhof', 'Pankow', 'Lichtenberg']

local_shops = []
for i in range(1, NUM_LOCAL_SHOPS + 1):
    city = random.choice(cities)
    local_shops.append({
        'shop_id': i,
        'shop_name': f"{random.choice(['Fresh', 'Quick', 'Daily', 'Express', 'Local', 'Prime'])} {random.choice(shop_types)} {i}",
        'shop_type': random.choice(shop_types),
        'city': city,
        'district': random.choice(districts),
        'partnership_start_date': random_date(datetime(2022, 1, 1), datetime(2024, 12, 31)),
        'commission_rate': round(random.uniform(0.10, 0.25), 2),
        'avg_preparation_time_minutes': random.randint(5, 20),
        'is_active': weighted_choice([True, False], [0.92, 0.08])
    })

df_shops = pd.DataFrame(local_shops)
print(f"   Created {len(df_shops)} local shops")

# 2. Generate Products
print("\n2. Generating products table...")
categories = {
    'Fresh Produce': ['Tomatoes', 'Lettuce', 'Carrots', 'Apples', 'Bananas', 'Oranges', 'Potatoes', 'Onions'],
    'Dairy': ['Milk', 'Cheese', 'Yogurt', 'Butter', 'Cream', 'Eggs'],
    'Meat & Fish': ['Chicken Breast', 'Ground Beef', 'Salmon', 'Pork Chops', 'Turkey', 'Shrimp'],
    'Bakery': ['Bread', 'Croissants', 'Baguette', 'Rolls', 'Cake', 'Cookies'],
    'Beverages': ['Water', 'Juice', 'Soda', 'Beer', 'Wine', 'Coffee', 'Tea'],
    'Pantry': ['Pasta', 'Rice', 'Canned Tomatoes', 'Olive Oil', 'Flour', 'Sugar', 'Salt'],
    'Snacks': ['Chips', 'Chocolate', 'Nuts', 'Crackers', 'Candy', 'Popcorn'],
    'Household': ['Toilet Paper', 'Paper Towels', 'Dish Soap', 'Laundry Detergent', 'Trash Bags']
}

products = []
product_id = 1
for category, items in categories.items():
    for item in items:
        for variant in range(random.randint(2, 5)):
            products.append({
                'product_id': product_id,
                'product_name': f"{item} {['Premium', 'Organic', 'Regular', 'Value', 'Fresh'][variant % 5]}",
                'category': category,
                'subcategory': item,
                'base_price': round(random.uniform(0.99, 29.99), 2),
                'unit': random.choice(['piece', 'kg', 'liter', 'pack', 'bottle'])
            })
            product_id += 1
            if product_id > NUM_PRODUCTS:
                break
        if product_id > NUM_PRODUCTS:
            break
    if product_id > NUM_PRODUCTS:
        break

df_products = pd.DataFrame(products)
print(f"   Created {len(df_products)} products across {len(categories)} categories")

# 3. Generate Customers
print("\n3. Generating customers table...")
customer_segments = ['New', 'Regular', 'VIP', 'Churned']
customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    registration_date = random_date(datetime(2022, 1, 1), datetime(2025, 12, 31))
    customers.append({
        'customer_id': i,
        'registration_date': registration_date,
        'city': random.choice(cities),
        'customer_segment': weighted_choice(customer_segments, [0.25, 0.45, 0.20, 0.10]),
        'total_orders': 0,  # Will be updated after orders
        'total_spent': 0.0,  # Will be updated after orders
        'last_order_date': None  # Will be updated after orders
    })

df_customers = pd.DataFrame(customers)
print(f"   Created {len(df_customers)} customers")

# 4. Generate Orders
print("\n4. Generating orders table...")
order_statuses = ['Delivered', 'Cancelled', 'In Progress']
payment_methods = ['Credit Card', 'Debit Card', 'PayPal', 'Cash']

orders = []
order_items = []
deliveries = []

for i in range(1, NUM_ORDERS + 1):
    customer = df_customers.sample(1).iloc[0]
    shop = df_shops[df_shops['is_active'] == True].sample(1).iloc[0]
    
    order_date = random_date(START_DATE, END_DATE)
    status = weighted_choice(order_statuses, [0.88, 0.07, 0.05])
    
    # Generate order items
    num_items = weighted_choice([1, 2, 3, 4, 5], [0.30, 0.30, 0.20, 0.15, 0.05])
    selected_products = df_products.sample(num_items)
    
    subtotal = 0
    for _, product in selected_products.iterrows():
        quantity = random.randint(1, 3)
        price = product['base_price']
        item_total = price * quantity
        subtotal += item_total
        
        order_items.append({
            'order_item_id': len(order_items) + 1,
            'order_id': i,
            'product_id': product['product_id'],
            'quantity': quantity,
            'unit_price': price,
            'total_price': round(item_total, 2)
        })
    
    # Apply random discount
    discount = 0
    if random.random() < 0.15:  # 15% chance of discount
        discount = round(subtotal * random.uniform(0.05, 0.20), 2)
    
    delivery_fee = weighted_choice([0, 1.99, 2.99], [0.40, 0.40, 0.20])
    total_amount = round(subtotal - discount + delivery_fee, 2)
    
    orders.append({
        'order_id': i,
        'customer_id': customer['customer_id'],
        'shop_id': shop['shop_id'],
        'order_date': order_date,
        'status': status,
        'subtotal': round(subtotal, 2),
        'discount': discount,
        'delivery_fee': delivery_fee,
        'total_amount': total_amount,
        'payment_method': random.choice(payment_methods)
    })
    
    # Generate delivery record if delivered
    if status == 'Delivered':
        prep_time = shop['avg_preparation_time_minutes'] + random.randint(-3, 5)
        delivery_time = random.randint(15, 45)
        
        deliveries.append({
            'delivery_id': len(deliveries) + 1,
            'order_id': i,
            'preparation_time_minutes': max(prep_time, 3),
            'delivery_time_minutes': delivery_time,
            'total_time_minutes': prep_time + delivery_time,
            'delivery_rating': weighted_choice([3, 4, 5], [0.10, 0.30, 0.60]) if random.random() < 0.70 else None
        })

df_orders = pd.DataFrame(orders)
df_order_items = pd.DataFrame(order_items)
df_deliveries = pd.DataFrame(deliveries)

print(f"   Created {len(df_orders)} orders")
print(f"   Created {len(df_order_items)} order items")
print(f"   Created {len(df_deliveries)} delivery records")

# Update customer statistics
print("\n5. Updating customer statistics...")
customer_stats = df_orders[df_orders['status'] == 'Delivered'].groupby('customer_id').agg({
    'order_id': 'count',
    'total_amount': 'sum',
    'order_date': 'max'
}).reset_index()
customer_stats.columns = ['customer_id', 'total_orders', 'total_spent', 'last_order_date']

df_customers = df_customers.merge(customer_stats, on='customer_id', how='left', suffixes=('', '_new'))
df_customers['total_orders'] = df_customers['total_orders_new'].fillna(0).astype(int)
df_customers['total_spent'] = df_customers['total_spent_new'].fillna(0).round(2)
df_customers['last_order_date'] = df_customers['last_order_date_new']
df_customers = df_customers.drop(columns=['total_orders_new', 'total_spent_new', 'last_order_date_new'])

# 6. Generate Inventory
print("\n6. Generating inventory table...")
inventory = []
for shop_id in df_shops[df_shops['is_active'] == True]['shop_id']:
    # Each shop carries 60-80% of products
    num_products_in_shop = int(len(df_products) * random.uniform(0.60, 0.80))
    shop_products = df_products.sample(num_products_in_shop)
    
    for _, product in shop_products.iterrows():
        stock_level = random.randint(0, 150)
        inventory.append({
            'inventory_id': len(inventory) + 1,
            'shop_id': shop_id,
            'product_id': product['product_id'],
            'stock_level': stock_level,
            'reorder_point': random.randint(10, 30),
            'last_restocked': random_date(datetime(2026, 1, 1), datetime(2026, 2, 13)),
            'is_available': stock_level > 0
        })

df_inventory = pd.DataFrame(inventory)
print(f"   Created {len(df_inventory)} inventory records")

# 7. Generate Promotions
print("\n7. Generating promotions table...")
promotion_types = ['Percentage Discount', 'Fixed Amount', 'Free Delivery', 'BOGO']
promotions = []
for i in range(1, 51):
    start_date = random_date(datetime(2024, 1, 1), datetime(2026, 1, 31))
    duration = random.randint(3, 21)
    end_date = start_date + timedelta(days=duration)
    
    promo_type = random.choice(promotion_types)
    if promo_type == 'Percentage Discount':
        discount_value = random.choice([5, 10, 15, 20, 25])
    elif promo_type == 'Fixed Amount':
        discount_value = random.choice([2, 3, 5, 10])
    else:
        discount_value = 0
    
    promotions.append({
        'promotion_id': i,
        'promotion_name': f"{promo_type} - {random.choice(['Weekend', 'Flash', 'Weekly', 'Special', 'Holiday'])} Deal {i}",
        'promotion_type': promo_type,
        'discount_value': discount_value,
        'start_date': start_date,
        'end_date': end_date,
        'min_order_value': random.choice([0, 15, 20, 25, 30]),
        'total_uses': random.randint(50, 5000),
        'total_revenue_impact': round(random.uniform(500, 50000), 2)
    })

df_promotions = pd.DataFrame(promotions)
print(f"   Created {len(df_promotions)} promotions")

# Save all datasets to CSV
print("\n8. Saving datasets to CSV files...")
output_dir = '.'

df_shops.to_csv(f'{output_dir}/local_shops.csv', index=False)
df_products.to_csv(f'{output_dir}/products.csv', index=False)
df_customers.to_csv(f'{output_dir}/customers.csv', index=False)
df_orders.to_csv(f'{output_dir}/orders.csv', index=False)
df_order_items.to_csv(f'{output_dir}/order_items.csv', index=False)
df_deliveries.to_csv(f'{output_dir}/deliveries.csv', index=False)
df_inventory.to_csv(f'{output_dir}/inventory.csv', index=False)
df_promotions.to_csv(f'{output_dir}/promotions.csv', index=False)

print("\n" + "=" * 60)
print("Dataset Generation Complete!")
print("=" * 60)
print("\nDataset Summary:")
print(f"  Local Shops: {len(df_shops):,}")
print(f"  Products: {len(df_products):,}")
print(f"  Customers: {len(df_customers):,}")
print(f"  Orders: {len(df_orders):,}")
print(f"  Order Items: {len(df_order_items):,}")
print(f"  Deliveries: {len(df_deliveries):,}")
print(f"  Inventory Records: {len(df_inventory):,}")
print(f"  Promotions: {len(df_promotions):,}")
print("\nKey Statistics:")
print(f"  Date Range: {START_DATE.date()} to {END_DATE.date()}")
print(f"  Total GMV: €{df_orders[df_orders['status']=='Delivered']['total_amount'].sum():,.2f}")
print(f"  Average Order Value: €{df_orders[df_orders['status']=='Delivered']['total_amount'].mean():.2f}")
print(f"  Order Completion Rate: {(df_orders['status']=='Delivered').sum()/len(df_orders)*100:.1f}%")
print(f"  Active Shops: {df_shops['is_active'].sum()}")
print(f"  Product Categories: {df_products['category'].nunique()}")
print("\nAll CSV files saved to: /home/ubuntu/quickshop-analytics/data/")
