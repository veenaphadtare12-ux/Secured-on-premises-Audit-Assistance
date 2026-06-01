import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont

# Create our Secure File Server directories
os.makedirs('audit_files/policies', exist_ok=True)
os.makedirs('audit_files/receipts', exist_ok=True)

def create_policy_pdfs():
    print("Generating Corporate Policy Documents...")
    
    # Document 1: Travel & Expense Policy
    c1 = canvas.Canvas("audit_files/policies/Travel_Expense_Policy_2026.pdf", pagesize=letter)
    c1.setFont("Helvetica-Bold", 16)
    c1.drawString(72, 750, "Global Travel & Expense Policy - v2.4")
    
    c1.setFont("Helvetica", 12)
    travel_rules = [
        "1. Preferred Airlines: Employees must use AirIndia or IndiGo for domestic travel.",
        "2. Budget Limits: Any single travel expense exceeding $1,000.00 strictly",
        "   requires documented pre-approval from a Vice President.",
        "3. Food & Beverage: Daily per diem is capped at $75.00.",
        "4. Audit Compliance: All physical or digital receipts must exactly match",
        "   the amounts logged in the central SQL ledger. Discrepancies are considered",
        "   fraudulent."
    ]
    
    y = 700
    for rule in travel_rules:
        c1.drawString(72, y, rule)
        y -= 25
    c1.save()

    # Document 2: IT Hardware Procurement
    c2 = canvas.Canvas("audit_files/policies/IT_Procurement_Policy.pdf", pagesize=letter)
    c2.setFont("Helvetica-Bold", 16)
    c2.drawString(72, 750, "IT Hardware Procurement Guidelines")
    
    c2.setFont("Helvetica", 12)
    it_rules = [
        "1. Approved Vendors: Meta Industries, Dell India, Cisco Systems.",
        "2. Hardware Caps: Standard server rack procurement is capped at $1,000.",
        "3. Software Subscriptions: Must be billed annually, not monthly.",
        "4. Asset Tagging: All hardware over $500 must be physically tagged within",
        "   48 hours of receipt."
    ]
    
    y = 700
    for rule in it_rules:
        c2.drawString(72, y, rule)
        y -= 25
    c2.save()
    
    print("Created: Travel_Expense_Policy_2026.pdf")
    print("Created: IT_Procurement_Policy.pdf")

def create_receipt_images():
    print("Generating Scanned Receipt Images (Targets & Noise)...")
    
    receipts_data = [
        # The Targets 
        ("TXN-1003", "AIRINDIA AIRWAYS", "Passenger: Corp Employee", "1250.00", "Match, but Policy Violation!"),
        ("TXN-1004", "META INDUSTRIES", "Item: Enterprise Server Rack", "990.00", "Fraud! DB says $890."),
        
        # The Noise 
        ("TXN-1001", "BLUEDART LOGISTICS", "Weight: 14kg - Express", "450.00", "Clean"),
        ("TXN-1002", "TIC HOLDINGS", "Consulting Retainer - March", "5000.00", "Clean"),
        ("TXN-1005", "HIGHGARDEN CATERING", "Office Lunch Catering", "210.50", "Clean")
    ]

    for txn, vendor, desc, amount, note in receipts_data:
        # Create a basic blank image looking like a piece of paper
        img = Image.new('RGB', (400, 450), color=(250, 250, 250))
        d = ImageDraw.Draw(img)
        
        # Draw some lines to make it look like a printed receipt
        d.line([(20, 80), (380, 80)], fill=(100, 100, 100), width=2)
        d.line([(20, 320), (380, 320)], fill=(100, 100, 100), width=2)
        
        # Text layout
        d.text((40, 40), f"{vendor} - INVOICE", fill=(0,0,0))
        d.text((40, 100), f"Receipt Ref: {txn}", fill=(0,0,0))
        d.text((40, 140), f"Date: 2026-03-XX", fill=(50,50,50))
        d.text((40, 200), f"Description:\n{desc}", fill=(0,0,0))
        
        d.text((40, 350), f"TOTAL BILLED: ${amount}", fill=(0,0,0))
        
        filename = f'audit_files/receipts/receipt_{txn}.png'
        img.save(filename)
        print(f"🧾 Created: {filename} ({note})")

if __name__ == "__main__":
    create_policy_pdfs()
    create_receipt_images()
    print("\n Enterprise Unstructured Data generated successfully in /audit_files.")