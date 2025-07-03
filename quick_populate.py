#!/usr/bin/env python3
"""
Quick script to populate minimal sample data
"""

from sqlalchemy.orm import sessionmaker
from database import engine
from models.database_models import Company, Insider, Transaction
from datetime import datetime, timedelta

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_minimal_data():
    """Create minimal sample data quickly."""
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Company).count() > 0:
            print("Data already exists.")
            return
        
        print("Creating minimal sample data...")
        
        # Create 3 companies
        companies = [
            Company(name="Shopify Inc.", symbol="SHOP", sector="Technology", market_cap=85000000000, exchange="TSX"),
            Company(name="Royal Bank of Canada", symbol="RY", sector="Financial Services", market_cap=180000000000, exchange="TSX"),
            Company(name="Canadian National Railway", symbol="CNR", sector="Transportation", market_cap=95000000000, exchange="TSX")
        ]
        
        for company in companies:
            db.add(company)
        db.commit()
        
        # Create 2 insiders per company
        insiders = []
        for company in companies:
            insider1 = Insider(name=f"CEO of {company.name}", title="Chief Executive Officer", company_id=company.id)
            insider2 = Insider(name=f"CFO of {company.name}", title="Chief Financial Officer", company_id=company.id)
            insiders.extend([insider1, insider2])
            db.add(insider1)
            db.add(insider2)
        db.commit()
        
        # Create 2 transactions per insider
        for insider in insiders:
            # Buy transaction
            buy_tx = Transaction(
                insider_id=insider.id,
                company_id=insider.company_id,
                transaction_date=datetime.now() - timedelta(days=30),
                transaction_type="buy",
                shares=1000,
                price_per_share=50.0,
                total_value=50000.0,
                filing_date=datetime.now() - timedelta(days=25)
            )
            
            # Sell transaction
            sell_tx = Transaction(
                insider_id=insider.id,
                company_id=insider.company_id,
                transaction_date=datetime.now() - timedelta(days=10),
                transaction_type="sell",
                shares=500,
                price_per_share=55.0,
                total_value=27500.0,
                filing_date=datetime.now() - timedelta(days=5)
            )
            
            db.add(buy_tx)
            db.add(sell_tx)
        
        db.commit()
        
        print("✅ Minimal data created successfully!")
        print(f"  - {len(companies)} companies")
        print(f"  - {len(insiders)} insiders")
        print(f"  - {len(insiders) * 2} transactions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_minimal_data()