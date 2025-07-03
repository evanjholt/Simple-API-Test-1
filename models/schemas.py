from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class Exchange(str, Enum):
    TSX = "TSX"
    TSXV = "TSXV"
    CSE = "CSE"
    NEO = "NEO"

# Company schemas
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Company name")
    symbol: str = Field(..., min_length=1, max_length=10, description="Trading symbol")
    sector: Optional[str] = Field(None, max_length=100, description="Business sector")
    market_cap: Optional[float] = Field(None, gt=0, description="Market capitalization")
    exchange: Exchange = Field(Exchange.TSX, description="Stock exchange")

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    sector: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[float] = Field(None, gt=0)
    exchange: Optional[Exchange] = None

class Company(CompanyBase):
    id: int
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True

# Insider schemas
class InsiderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Insider's full name")
    title: Optional[str] = Field(None, max_length=200, description="Position/title")
    company_id: int = Field(..., gt=0, description="Company ID")

class InsiderCreate(InsiderBase):
    pass

class InsiderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    title: Optional[str] = Field(None, max_length=200)
    company_id: Optional[int] = Field(None, gt=0)

class Insider(InsiderBase):
    id: int
    created_at: datetime
    is_active: bool = True
    company: Optional[Company] = None

    class Config:
        from_attributes = True

# Transaction schemas
class TransactionBase(BaseModel):
    insider_id: int = Field(..., gt=0, description="Insider ID")
    company_id: int = Field(..., gt=0, description="Company ID")
    transaction_date: datetime = Field(..., description="Date of transaction")
    transaction_type: TransactionType = Field(..., description="Buy or sell")
    shares: int = Field(..., gt=0, description="Number of shares")
    price_per_share: float = Field(..., gt=0, description="Price per share")
    total_value: float = Field(..., gt=0, description="Total transaction value")
    filing_date: datetime = Field(..., description="Date filed with regulators")
    notes: Optional[str] = Field(None, description="Additional notes")

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    transaction_date: Optional[datetime] = None
    transaction_type: Optional[TransactionType] = None
    shares: Optional[int] = Field(None, gt=0)
    price_per_share: Optional[float] = Field(None, gt=0)
    total_value: Optional[float] = Field(None, gt=0)
    filing_date: Optional[datetime] = None
    notes: Optional[str] = None

class Transaction(TransactionBase):
    id: int
    created_at: datetime
    insider: Optional[Insider] = None
    company: Optional[Company] = None

    class Config:
        from_attributes = True

# Response schemas
class HTTPError(BaseModel):
    detail: str

class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    per_page: int
    pages: int

# Statistics schemas
class TransactionStats(BaseModel):
    total_transactions: int
    total_buy_value: float
    total_sell_value: float
    net_value: float
    most_active_insider: Optional[str] = None
    most_active_company: Optional[str] = None