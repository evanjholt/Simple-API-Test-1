from typing import List, Optional
from fastapi import APIRouter, Query, Path, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, date
from models.schemas import Transaction, TransactionCreate, TransactionUpdate, SuccessResponse, PaginatedResponse, TransactionType, TransactionStats
from models.database_models import Transaction as DBTransaction, Insider as DBInsider, Company as DBCompany
from utils.exceptions import TransactionNotFoundError, InsiderNotFoundError, CompanyNotFoundError
from database import get_db

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/", response_model=PaginatedResponse, summary="Get all transactions")
async def get_transactions(
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of transactions to return"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    company_id: Optional[int] = Query(None, gt=0, description="Filter by company ID"),
    insider_id: Optional[int] = Query(None, gt=0, description="Filter by insider ID"),
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    min_value: Optional[float] = Query(None, ge=0, description="Minimum transaction value"),
    max_value: Optional[float] = Query(None, ge=0, description="Maximum transaction value"),
    db: Session = Depends(get_db)
):
    query = db.query(DBTransaction)
    
    if transaction_type:
        query = query.filter(DBTransaction.transaction_type == transaction_type)
    
    if company_id:
        query = query.filter(DBTransaction.company_id == company_id)
    
    if insider_id:
        query = query.filter(DBTransaction.insider_id == insider_id)
    
    if start_date:
        query = query.filter(DBTransaction.transaction_date >= start_date)
    
    if end_date:
        query = query.filter(DBTransaction.transaction_date <= end_date)
    
    if min_value is not None:
        query = query.filter(DBTransaction.total_value >= min_value)
    
    if max_value is not None:
        query = query.filter(DBTransaction.total_value <= max_value)
    
    query = query.order_by(desc(DBTransaction.transaction_date))
    
    total = query.count()
    transactions = query.offset(skip).limit(limit).all()
    
    return PaginatedResponse(
        items=[{
            "id": t.id, "insider_id": t.insider_id, "company_id": t.company_id,
            "transaction_date": t.transaction_date, "transaction_type": t.transaction_type,
            "shares": t.shares, "price_per_share": t.price_per_share, "total_value": t.total_value,
            "filing_date": t.filing_date, "notes": t.notes, "created_at": t.created_at
        } for t in transactions],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{transaction_id}", response_model=Transaction, summary="Get transaction by ID")
async def get_transaction(
    transaction_id: int = Path(..., gt=0, description="The ID of the transaction to retrieve"),
    db: Session = Depends(get_db)
):
    transaction = db.query(DBTransaction).filter(DBTransaction.id == transaction_id).first()
    if not transaction:
        raise TransactionNotFoundError(transaction_id)
    return transaction

@router.post("/", response_model=Transaction, status_code=201, summary="Create a new transaction")
async def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    insider = db.query(DBInsider).filter(DBInsider.id == transaction.insider_id).first()
    if not insider:
        raise InsiderNotFoundError(transaction.insider_id)
    
    company = db.query(DBCompany).filter(DBCompany.id == transaction.company_id).first()
    if not company:
        raise CompanyNotFoundError(transaction.company_id)
    
    db_transaction = DBTransaction(
        insider_id=transaction.insider_id,
        company_id=transaction.company_id,
        transaction_date=transaction.transaction_date,
        transaction_type=transaction.transaction_type,
        shares=transaction.shares,
        price_per_share=transaction.price_per_share,
        total_value=transaction.total_value,
        filing_date=transaction.filing_date,
        notes=transaction.notes
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.put("/{transaction_id}", response_model=Transaction, summary="Update transaction")
async def update_transaction(
    transaction_update: TransactionUpdate,
    transaction_id: int = Path(..., gt=0, description="The ID of the transaction to update"),
    db: Session = Depends(get_db)
):
    transaction = db.query(DBTransaction).filter(DBTransaction.id == transaction_id).first()
    if not transaction:
        raise TransactionNotFoundError(transaction_id)
    
    update_data = transaction_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/{transaction_id}", response_model=SuccessResponse, summary="Delete transaction")
async def delete_transaction(
    transaction_id: int = Path(..., gt=0, description="The ID of the transaction to delete"),
    db: Session = Depends(get_db)
):
    transaction = db.query(DBTransaction).filter(DBTransaction.id == transaction_id).first()
    if not transaction:
        raise TransactionNotFoundError(transaction_id)
    
    db.delete(transaction)
    db.commit()
    
    return SuccessResponse(
        message=f"Transaction {transaction_id} deleted successfully",
        data={"deleted_transaction_id": transaction_id}
    )

@router.get("/insider/{insider_id}", response_model=List[Transaction], summary="Get transactions by insider")
async def get_transactions_by_insider(
    insider_id: int = Path(..., gt=0, description="The ID of the insider"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of transactions"),
    db: Session = Depends(get_db)
):
    insider = db.query(DBInsider).filter(DBInsider.id == insider_id).first()
    if not insider:
        raise InsiderNotFoundError(insider_id)
    
    query = db.query(DBTransaction).filter(DBTransaction.insider_id == insider_id)
    if transaction_type:
        query = query.filter(DBTransaction.transaction_type == transaction_type)
    
    transactions = query.order_by(desc(DBTransaction.transaction_date)).limit(limit).all()
    return transactions

@router.get("/company/{company_id}", response_model=List[Transaction], summary="Get transactions by company")
async def get_transactions_by_company(
    company_id: int = Path(..., gt=0, description="The ID of the company"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of transactions"),
    db: Session = Depends(get_db)
):
    company = db.query(DBCompany).filter(DBCompany.id == company_id).first()
    if not company:
        raise CompanyNotFoundError(company_id)
    
    query = db.query(DBTransaction).filter(DBTransaction.company_id == company_id)
    if transaction_type:
        query = query.filter(DBTransaction.transaction_type == transaction_type)
    
    transactions = query.order_by(desc(DBTransaction.transaction_date)).limit(limit).all()
    return transactions

@router.get("/stats/", response_model=TransactionStats, summary="Get transaction statistics")
async def get_transaction_stats(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    query = db.query(DBTransaction)
    
    if start_date:
        query = query.filter(DBTransaction.transaction_date >= start_date)
    
    if end_date:
        query = query.filter(DBTransaction.transaction_date <= end_date)
    
    transactions = query.all()
    
    total_transactions = len(transactions)
    total_buy_value = sum(t.total_value for t in transactions if t.transaction_type == "buy")
    total_sell_value = sum(t.total_value for t in transactions if t.transaction_type == "sell")
    net_value = total_buy_value - total_sell_value
    
    # Find most active insider and company
    insider_counts = {}
    company_counts = {}
    
    for t in transactions:
        insider_counts[t.insider_id] = insider_counts.get(t.insider_id, 0) + 1
        company_counts[t.company_id] = company_counts.get(t.company_id, 0) + 1
    
    most_active_insider = None
    most_active_company = None
    
    if insider_counts:
        most_active_insider_id = max(insider_counts, key=insider_counts.get)
        insider = db.query(DBInsider).filter(DBInsider.id == most_active_insider_id).first()
        most_active_insider = insider.name if insider else None
    
    if company_counts:
        most_active_company_id = max(company_counts, key=company_counts.get)
        company = db.query(DBCompany).filter(DBCompany.id == most_active_company_id).first()
        most_active_company = company.name if company else None
    
    return TransactionStats(
        total_transactions=total_transactions,
        total_buy_value=total_buy_value,
        total_sell_value=total_sell_value,
        net_value=net_value,
        most_active_insider=most_active_insider,
        most_active_company=most_active_company
    )