from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    sector = Column(String(100), nullable=True)
    market_cap = Column(Float, nullable=True)
    exchange = Column(String(50), nullable=False, default="TSX")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    insiders = relationship("Insider", back_populates="company")
    transactions = relationship("Transaction", back_populates="company")

class Insider(Base):
    __tablename__ = "insiders"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    company = relationship("Company", back_populates="insiders")
    transactions = relationship("Transaction", back_populates="insider")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    insider_id = Column(Integer, ForeignKey("insiders.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # 'buy' or 'sell'
    shares = Column(Integer, nullable=False)
    price_per_share = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    filing_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    insider = relationship("Insider", back_populates="transactions")
    company = relationship("Company", back_populates="transactions")