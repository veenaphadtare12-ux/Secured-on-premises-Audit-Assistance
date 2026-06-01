import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

def initialize_enterprise_ledger(num_records=2500):
    print(f"Initializing Enterprise Database with {num_records} records...")
    
    conn = sqlite3.connect('corporate_ledger.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            transaction_id TEXT PRIMARY KEY,
            date TEXT,
            vendor TEXT,
            category TEXT,
            amount REAL,
            status TEXT
        )
    ''')
    cursor.execute('DELETE FROM expenses')

   
    transactions = [
        ('TXN-1001', '2026-03-01', 'Bluedart Logistics', 'Shipping', 450.00, 'Cleared'),
        ('TXN-1002', '2026-03-02', 'TIC Holdings', 'Consulting', 5000.00, 'Cleared'),
        ('TXN-1003', '2026-03-05', 'AirIndia Airways', 'Travel', 1250.00, 'Pending'), 
        ('TXN-1004', '2026-03-07', 'Meta Industries', 'Hardware', 890.00, 'Cleared'),   
        ('TXN-1005', '2026-03-09', 'Highgarden Catering', 'Food & Bev', 210.50, 'Cleared')
    ]


    vendors = {
        'Travel': ['AirIndia Airways', 'IndiGo', 'Taj Hotels', 'MakeMyTrip Corporate', 'Uber Corporate'],
        'Hardware': ['Meta Industries', 'Dell India', 'Lenovo Corporate', 'Cisco Systems', 'Reliance Digital'],
        'Software': ['AWS India', 'Microsoft Azure', 'Zoho Corporation', 'Atlassian', 'GitHub'],
        'Consulting': ['TCS', 'Infosys', 'McKinsey & Company', 'TIC Holdings', 'Wipro'],
        'Shipping': ['Bluedart Logistics', 'Delhivery', 'FedEx India', 'DHL'],
        'Food & Bev': ['Highgarden Catering', 'Swiggy Corporate', 'Zomato for Work', 'Starbucks Corporate']
    }
    statuses = ['Cleared', 'Cleared', 'Cleared', 'Cleared', 'Pending', 'Rejected']

    start_date = datetime(2025, 1, 1)
    
    # Generate 2,500 random transactions starting from TXN-1006
    for i in range(1006, 1006 + num_records):
        txn_id = f"TXN-{i}"
        
        # Random date within the last year
        random_days = random.randint(0, 400)
        txn_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')
        
        category = random.choice(list(vendors.keys()))
        vendor = random.choice(vendors[category])
        
        # Random amount between $10 and $4000
        amount = round(random.uniform(10.0, 4000.0), 2)
        status = random.choice(statuses)
        
        transactions.append((txn_id, txn_date, vendor, category, amount, status))

    random.shuffle(transactions)

    cursor.executemany('''
        INSERT INTO expenses (transaction_id, date, vendor, category, amount, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', transactions)
    conn.commit()
    
 
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    print("\nEnterprise Database created successfully.")
    print(f"Total Records: {len(df)}")
    print("-" * 75)
    print("Snapshot (First 10 rows):")
    print(df.head(10).to_string(index=False))
    print("-" * 75)

    conn.close()

if __name__ == "__main__":
    initialize_enterprise_ledger(2500)