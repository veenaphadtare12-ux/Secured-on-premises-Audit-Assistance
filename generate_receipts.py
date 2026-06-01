import pandas as pd
import random
import os
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import create_engine

# Connection to the Docker Database
DB_URI = "postgresql+psycopg2://audit_admin:secure_password_123@localhost:5432/corporate_ledger"
engine = create_engine(DB_URI)

RECEIPT_DIR = "audit_files/receipts"
os.makedirs(RECEIPT_DIR, exist_ok=True)

def create_receipt_image(txn_id, vendor, date, amount, filename):
    """Draws a raw, text-heavy image that Florence-2 can easily read."""
    # Create a blank white image resembling a paper receipt
    img = Image.new('RGB', (400, 500), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Text content designed for OCR
    text = f"""
    {vendor.upper()}
    -------------------------
    Receipt Ref: {txn_id}
    Date: {date}
    
    Description:
    Corporate Expense
    
    -------------------------
    TOTAL BILLED: ${amount:.2f}
    """
    
    # Draw the text 
    d.text((20, 20), text, fill=(0, 0, 0))
    img.save(f"{RECEIPT_DIR}/{filename}")

def generate_chaos_dataset():
    print("📥 Fetching ledger from PostgreSQL...")
    df = pd.read_sql("SELECT * FROM expenses", engine)
    
    # Pick 50 random transactions to generate files for, ensuring TXN-1004 is included
    demo_txns = df.sample(50)
    golden_record = df[df['transaction_id'] == 'TXN-1004']
    if not golden_record.empty:
        demo_txns = pd.concat([golden_record, demo_txns]).drop_duplicates()

    print(f"Generating {len(demo_txns)} synthetic physical receipts...")
    
    stats = {"matched": 0, "fraud": 0, "missing": 0}

    for _, row in demo_txns.iterrows():
        txn_id = row['transaction_id']
        vendor = row['vendor']
        date = row['date']
        db_amount = float(row['amount'])
        
        # Inject randomness
        chance = random.random()
        
        if txn_id == 'TXN-1004':
            # Preserving the demo fraud
            create_receipt_image(txn_id, vendor, date, db_amount + 100, f"receipt_{txn_id}.png")
            stats["fraud"] += 1
            
        elif chance < 0.15:
            # FRAUD 
            fraud_amount = db_amount + random.uniform(20, 500)
            create_receipt_image(txn_id, vendor, date, fraud_amount, f"receipt_{txn_id}.png")
            stats["fraud"] += 1
            print(f"   🚨 Fraud injected into {txn_id} (DB: ${db_amount:.2f}, Receipt: ${fraud_amount:.2f})")
            
        elif chance < 0.30:
            stats["missing"] += 1
            
        else:
            create_receipt_image(txn_id, vendor, date, db_amount, f"receipt_{txn_id}.png")
            stats["matched"] += 1

    print("\n Generation Complete!")
    print(f"Stats: {stats['matched']} Perfect | {stats['fraud']} Discrepancies | {stats['missing']} Missing Files")

if __name__ == "__main__":
    generate_chaos_dataset()