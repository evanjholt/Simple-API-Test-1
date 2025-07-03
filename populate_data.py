#!/usr/bin/env python3
"""
Script to populate the database with sample Canadian insider trading data.
"""

import asyncio
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import sessionmaker
from database import engine, Base
from models.database_models import Company, Insider, Transaction

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sample Canadian companies data
CANADIAN_COMPANIES = [
    {"name": "Shopify Inc.", "symbol": "SHOP", "sector": "Technology", "market_cap": 85000000000, "exchange": "TSX"},
    {"name": "Royal Bank of Canada", "symbol": "RY", "sector": "Financial Services", "market_cap": 180000000000, "exchange": "TSX"},
    {"name": "Canadian National Railway Company", "symbol": "CNR", "sector": "Transportation", "market_cap": 95000000000, "exchange": "TSX"},
    {"name": "Brookfield Asset Management Inc.", "symbol": "BAM", "sector": "Financial Services", "market_cap": 55000000000, "exchange": "TSX"},
    {"name": "Canadian Pacific Railway Limited", "symbol": "CP", "sector": "Transportation", "market_cap": 75000000000, "exchange": "TSX"},
    {"name": "Constellation Software Inc.", "symbol": "CSU", "sector": "Technology", "market_cap": 45000000000, "exchange": "TSX"},
    {"name": "Alimentation Couche-Tard Inc.", "symbol": "ATD", "sector": "Consumer Discretionary", "market_cap": 65000000000, "exchange": "TSX"},
    {"name": "Bank of Nova Scotia", "symbol": "BNS", "sector": "Financial Services", "market_cap": 80000000000, "exchange": "TSX"},
    {"name": "Nutrien Ltd.", "symbol": "NTR", "sector": "Materials", "market_cap": 35000000000, "exchange": "TSX"},
    {"name": "Wesdome Gold Mines Ltd.", "symbol": "WDO", "sector": "Materials", "market_cap": 1500000000, "exchange": "TSX"},
    {"name": "Lightspeed Commerce Inc.", "symbol": "LSPD", "sector": "Technology", "market_cap": 3500000000, "exchange": "TSX"},
    {"name": "Nuvei Corporation", "symbol": "NVEI", "sector": "Technology", "market_cap": 2800000000, "exchange": "TSX"},
    {"name": "Tilray Brands Inc.", "symbol": "TLRY", "sector": "Healthcare", "market_cap": 1200000000, "exchange": "TSX"},
    {"name": "Blackberry Limited", "symbol": "BB", "sector": "Technology", "market_cap": 2500000000, "exchange": "TSX"},
    {"name": "Canopy Growth Corporation", "symbol": "WEED", "sector": "Healthcare", "market_cap": 800000000, "exchange": "TSX"}
]

# Sample insider names and titles
INSIDER_NAMES = [
    "John Smith", "Sarah Johnson", "Michael Brown", "Emily Davis", "David Wilson",
    "Jennifer Miller", "Robert Garcia", "Lisa Rodriguez", "Christopher Martinez", "Amanda Taylor",
    "Matthew Anderson", "Jessica Thomas", "Daniel Jackson", "Ashley White", "James Harris",
    "Michelle Martin", "Ryan Thompson", "Stephanie Garcia", "Kevin Martinez", "Nicole Robinson",
    "Brandon Clark", "Samantha Lewis", "Justin Lee", "Rachel Walker", "Andrew Hall",
    "Megan Allen", "Tyler Young", "Lauren King", "Jonathan Wright", "Kayla Lopez"
]

INSIDER_TITLES = [
    "Chief Executive Officer", "Chief Financial Officer", "Chief Operating Officer",
    "Chief Technology Officer", "President", "Vice President", "Director",
    "Senior Vice President", "Executive Vice President", "Chief Marketing Officer",
    "Chief Legal Officer", "Chief Human Resources Officer", "Chief Strategy Officer",
    "General Manager", "Managing Director", "Board Member", "Independent Director"
]

def create_sample_data():
    """Create and populate the database with sample data."""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Company).count() > 0:
            print("Data already exists. Skipping population.")
            return
        
        print("Creating sample Canadian companies...")
        
        # Create companies
        companies = []
        for company_data in CANADIAN_COMPANIES:
            company = Company(
                name=company_data["name"],
                symbol=company_data["symbol"],
                sector=company_data["sector"],
                market_cap=company_data["market_cap"],
                exchange=company_data["exchange"]
            )
            companies.append(company)
            db.add(company)
        
        db.commit()
        print(f"Created {len(companies)} companies")
        
        # Create insiders (2-4 per company)
        print("Creating insiders...")
        insiders = []
        used_names = set()
        
        for company in companies:
            num_insiders = random.randint(2, 4)
            for _ in range(num_insiders):
                # Ensure unique names
                name = random.choice(INSIDER_NAMES)
                while name in used_names:
                    name = random.choice(INSIDER_NAMES)
                used_names.add(name)
                
                insider = Insider(
                    name=name,
                    title=random.choice(INSIDER_TITLES),
                    company_id=company.id
                )
                insiders.append(insider)
                db.add(insider)
        
        db.commit()
        print(f"Created {len(insiders)} insiders")
        
        # Create transactions (5-15 per insider over the last 2 years)
        print("Creating transactions...")
        transactions = []
        
        start_date = datetime.now() - timedelta(days=730)  # 2 years ago
        end_date = datetime.now()
        
        for insider in insiders:
            num_transactions = random.randint(5, 15)
            
            for _ in range(num_transactions):
                # Random transaction date within the last 2 years
                transaction_date = start_date + timedelta(
                    days=random.randint(0, (end_date - start_date).days)
                )
                
                # Filing date is usually 1-10 days after transaction date
                filing_date = transaction_date + timedelta(days=random.randint(1, 10))
                
                # Random transaction type (70% buy, 30% sell for realistic pattern)
                transaction_type = "buy" if random.random() < 0.7 else "sell"
                
                # Random number of shares and price
                shares = random.randint(100, 50000)
                
                # Price varies by company market cap (higher cap = higher price)
                company = next(c for c in companies if c.id == insider.company_id)
                if company.market_cap > 50000000000:  # Large cap
                    price_per_share = round(random.uniform(50, 300), 2)
                elif company.market_cap > 10000000000:  # Mid cap
                    price_per_share = round(random.uniform(20, 100), 2)
                else:  # Small cap
                    price_per_share = round(random.uniform(2, 50), 2)
                
                total_value = shares * price_per_share
                
                # Random notes (sometimes)
                notes = None
                if random.random() < 0.3:  # 30% chance of having notes
                    note_options = [
                        "Automatic exercise of stock options",
                        "Disposition pursuant to 10b5-1 plan",
                        "Gift to family member",
                        "Estate planning transaction",
                        "Tax withholding",
                        "Exercise of warrants"
                    ]
                    notes = random.choice(note_options)
                
                transaction = Transaction(
                    insider_id=insider.id,
                    company_id=insider.company_id,
                    transaction_date=transaction_date,
                    transaction_type=transaction_type,
                    shares=shares,
                    price_per_share=price_per_share,
                    total_value=total_value,
                    filing_date=filing_date,
                    notes=notes
                )
                transactions.append(transaction)
                db.add(transaction)
        
        db.commit()
        print(f"Created {len(transactions)} transactions")
        
        print("\\n✅ Database populated successfully!")
        print(f"Summary:")
        print(f"  - {len(companies)} Canadian companies")
        print(f"  - {len(insiders)} corporate insiders") 
        print(f"  - {len(transactions)} trading transactions")
        print(f"  - Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Show some statistics
        buy_transactions = [t for t in transactions if t.transaction_type == "buy"]
        sell_transactions = [t for t in transactions if t.transaction_type == "sell"]
        total_buy_value = sum(t.total_value for t in buy_transactions)
        total_sell_value = sum(t.total_value for t in sell_transactions)
        
        print(f"\\nTransaction Statistics:")
        print(f"  - Buy transactions: {len(buy_transactions)} (${total_buy_value:,.2f})")
        print(f"  - Sell transactions: {len(sell_transactions)} (${total_sell_value:,.2f})")
        print(f"  - Net insider buying: ${total_buy_value - total_sell_value:,.2f}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()