import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine

fake = Faker()

# Database Connection String
DB_URI = "postgresql+psycopg2://audit_admin:secure_password_123@localhost:5432/corporate_ledger"
engine = create_engine(DB_URI)

# Realistic Corporate Seed Data
CATEGORIES = {
    'Software': ['Cloudflare', 'AWS', 'GitHub', 'Atlassian', 'Microsoft'],
    'Hardware': ['Dell', 'Apple', 'Nvidia', 'Cisco'],
    'Travel': ['Delta Airlines', 'Marriott', 'Uber', 'United Airlines'],
    'Food & Bev': ['Starbucks', 'Caterer Inc', 'DoorDash Corporate'],
    'Consulting': ['McKinsey', 'Deloitte', 'Accenture'],
    'Shipping': ['FedEx', 'UPS', 'DHL']
}

def generate_synthetic_data(num_records=1000):
    print(f"Generating {num_records} synthetic transactions...")
    data = []
    
    # Demo transaction
    data.append({
        "transaction_id": "TXN-1004",
        "date": "2026-03-10",
        "vendor": "Meta Industries",
        "category": "Hardware",
        "amount": 890.00,  
        "status": "cleared"
    })

    # Generates random historical data (Sep 2025 to March 2026)
    start_date = datetime(2025, 9, 1) 
    end_date = datetime(2026, 3, 14)

    for i in range(1005, 1005 + num_records):
        category = random.choice(list(CATEGORIES.keys()))
        vendor = random.choice(CATEGORIES[category])
        
        # Random date
        random_days = random.randint(0, (end_date - start_date).days)
        txn_date = start_date + timedelta(days=random_days)
        
        # Realistic amounts based on category
        if category in ['Software', 'Hardware', 'Consulting', 'Shipping']:
            amount = round(random.uniform(1000.0, 25000.0), 2)
        else:
            amount = round(random.uniform(50.0, 3000.0), 2)

        data.append({
            "transaction_id": f"TXN-{i}",
            "date": txn_date.strftime("%Y-%m-%d"),
            "vendor": vendor,
            "category": category,
            "amount": amount,
            "status": "cleared"
        })

    return pd.DataFrame(data)

def ingest_data(df, table_name="expenses"):
    # Demo reset
    print(f"📥 Ingesting {len(df)} rows into PostgreSQL '{table_name}' table...")
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print("Data ingestion complete! Database is ready for demos.")
    except Exception as e:
        print(f"Ingestion failed: {e}")

if __name__ == "__main__":
    # Generate 1,500 rows of highly realistic data
    synthetic_df = generate_synthetic_data(1500)
    ingest_data(synthetic_df)