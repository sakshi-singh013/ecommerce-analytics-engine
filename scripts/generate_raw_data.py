import os
import json
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

# Ensure directories exist
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🚀 Starting synthetic raw e-commerce data generation...")

# Configuration
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 50
NUM_ORDERS = 3500
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2026, 3, 1)

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

# ---------------------------------------------------------
# 1. GENERATE CUSTOMERS
# ---------------------------------------------------------
print("Generating Customers dataset...")
channels = ['Organic Search', 'Paid Ads', 'Social Media', 'Email Campaign', 'Referral']
countries = ['United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'India', 'Australia']

customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    signup_dt = random_date(START_DATE, END_DATE - timedelta(days=30))
    customers.append({
        'customer_id': f"CUST_{i:05d}",
        'full_name': fake.name(),
        'email': fake.email(),
        'country': random.choice(countries),
        'signup_timestamp': signup_dt.strftime('%Y-%m-%d %H:%M:%S'),
        'acquisition_channel': random.choice(channels)
    })

df_customers = pd.DataFrame(customers)
df_customers.to_csv(os.path.join(OUTPUT_DIR, "raw_customers.csv"), index=False)

# ---------------------------------------------------------
# 2. GENERATE PRODUCTS
# ---------------------------------------------------------
print("Generating Products dataset...")
categories = {
    'Electronics': [('Wireless Earbuds', 79.99, 35.00), ('Smart Watch', 199.99, 90.00), ('Mechanical Keyboard', 129.99, 55.00), ('Gaming Mouse', 49.99, 20.00), ('USB-C Hub', 39.99, 15.00)],
    'Apparel': [('Denim Jacket', 89.99, 30.00), ('Cotton T-Shirt', 24.99, 8.00), ('Running Shoes', 119.99, 45.00), ('Leather Belt', 34.99, 10.00), ('Hoodie', 59.99, 22.00)],
    'Home & Kitchen': [('Coffee Maker', 149.99, 65.00), ('Air Fryer', 110.00, 48.00), ('Blender', 69.99, 25.00), ('Stainless Mug', 19.99, 6.00), ('Desk Lamp', 29.99, 11.00)],
    'Beauty': [('Face Serum', 39.99, 12.00), ('Moisturizer', 29.99, 8.00), ('Sunscreen SPF 50', 22.99, 6.00), ('Shampoo Set', 34.99, 10.00), ('Perfume 50ml', 85.00, 25.00)]
}

products = []
prod_id = 1
for cat, items in categories.items():
    for name, price, cost in items:
        products.append({
            'product_id': f"PROD_{prod_id:04d}",
            'product_name': name,
            'category': cat,
            'price': price,
            'cost_price': cost,
            'stock_level': random.randint(10, 500)
        })
        prod_id += 1

df_products = pd.DataFrame(products)
df_products.to_csv(os.path.join(OUTPUT_DIR, "raw_products.csv"), index=False)

# ---------------------------------------------------------
# 3. GENERATE ORDERS & ORDER ITEMS
# ---------------------------------------------------------
print("Generating Orders and Order Items dataset...")
payment_methods = ['Credit Card', 'PayPal', 'Apple Pay', 'UPI', 'Buy Now Pay Later']
statuses = ['Completed', 'Completed', 'Completed', 'Completed', 'Refunded', 'Cancelled']

orders = []
order_items = []
item_id_counter = 1

for order_id_num in range(1, NUM_ORDERS + 1):
    cust = random.choice(customers)
    cust_id = cust['customer_id']
    cust_signup = datetime.strptime(cust['signup_timestamp'], '%Y-%m-%d %H:%M:%S')
    
    order_dt = random_date(cust_signup, END_DATE)
    status = random.choice(statuses)
    
    num_items = random.choices([1, 2, 3, 4], weights=[0.5, 0.3, 0.15, 0.05])[0]
    selected_products = random.sample(products, num_items)
    
    order_id = f"ORD_{order_id_num:06d}"
    discount = round(random.choice([0.0, 0.0, 0.0, 5.0, 10.0, 15.0]), 2)
    shipping = round(random.choice([0.0, 4.99, 9.99]), 2)
    
    orders.append({
        'order_id': order_id,
        'customer_id': cust_id,
        'order_timestamp': order_dt.strftime('%Y-%m-%d %H:%M:%S'),
        'payment_method': random.choice(payment_methods),
        'order_status': status,
        'shipping_cost': shipping,
        'discount_amount': discount
    })
    
    for prod in selected_products:
        qty = random.randint(1, 3)
        order_items.append({
            'order_item_id': f"ITEM_{item_id_counter:07d}",
            'order_id': order_id,
            'product_id': prod['product_id'],
            'quantity': qty,
            'unit_price': prod['price']
        })
        item_id_counter += 1

df_orders = pd.DataFrame(orders)
df_orders.to_csv(os.path.join(OUTPUT_DIR, "raw_orders.csv"), index=False)

df_order_items = pd.DataFrame(order_items)
df_order_items.to_csv(os.path.join(OUTPUT_DIR, "raw_order_items.csv"), index=False)

# ---------------------------------------------------------
# 4. GENERATE CLICKSTREAM WEB SESSIONS (JSON)
# ---------------------------------------------------------
print("Generating Clickstream Web Sessions dataset (JSON)...")
devices = ['Desktop', 'Mobile-iOS', 'Mobile-Android', 'Tablet']
pages = ['home', 'category_view', 'product_detail', 'cart', 'checkout', 'order_confirmation']

web_sessions = []
for session_num in range(1, 6000):
    cust = random.choice(customers)
    sess_dt = random_date(START_DATE, END_DATE)
    device = random.choice(devices)
    
    # Simulate realistic funnel progression
    is_buyer = random.random() < 0.35
    funnel_depth = 6 if is_buyer else random.randint(1, 4)
    
    events = []
    for step in range(funnel_depth):
        event_time = sess_dt + timedelta(seconds=step * random.randint(15, 120))
        page = pages[step]
        events.append({
            'event_timestamp': event_time.strftime('%Y-%m-%d %H:%M:%S'),
            'page': page,
            'product_viewed': random.choice(products)['product_id'] if page == 'product_detail' else None
        })
        
    web_sessions.append({
        'session_id': f"SESS_{session_num:06d}",
        'customer_id': cust['customer_id'],
        'device_type': device,
        'session_start': sess_dt.strftime('%Y-%m-%d %H:%M:%S'),
        'event_count': len(events),
        'completed_purchase': is_buyer,
        'events': events
    })

with open(os.path.join(OUTPUT_DIR, "raw_web_sessions.json"), "w") as f:
    json.dump(web_sessions, f, indent=2)

print(f"✅ Successfully generated all raw datasets in: {OUTPUT_DIR}")
