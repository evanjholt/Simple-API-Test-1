from typing import List, Optional
from fastapi import APIRouter, Query, Path, HTTPException, Depends
from sqlalchemy.orm import Session
from models.schemas import Company, CompanyCreate, CompanyUpdate, SuccessResponse, PaginatedResponse, Exchange
from models.database_models import Company as DBCompany
from utils.exceptions import CompanyNotFoundError
from database import get_db

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=PaginatedResponse, summary="Get all companies")
async def get_companies(
    skip: int = Query(0, ge=0, description="Number of companies to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of companies to return"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    exchange: Optional[Exchange] = Query(None, description="Filter by exchange"),
    min_market_cap: Optional[float] = Query(None, ge=0, description="Minimum market cap filter"),
    max_market_cap: Optional[float] = Query(None, ge=0, description="Maximum market cap filter"),
    active_only: bool = Query(False, description="Show only active companies"),
    db: Session = Depends(get_db)
):
    query = db.query(DBCompany)
    
    if sector:
        query = query.filter(DBCompany.sector.ilike(f"%{sector}%"))
    
    if exchange:
        query = query.filter(DBCompany.exchange == exchange)
    
    if min_market_cap is not None:
        query = query.filter(DBCompany.market_cap >= min_market_cap)
    
    if max_market_cap is not None:
        query = query.filter(DBCompany.market_cap <= max_market_cap)
    
    if active_only:
        query = query.filter(DBCompany.is_active == True)
    
    total = query.count()
    companies = query.offset(skip).limit(limit).all()
    
    return PaginatedResponse(
        items=[{"id": c.id, "name": c.name, "symbol": c.symbol, "sector": c.sector, "market_cap": c.market_cap, "exchange": c.exchange, "created_at": c.created_at, "is_active": c.is_active} for c in companies],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{company_id}", response_model=Company, summary="Get company by ID")
async def get_company(
    company_id: int = Path(..., gt=0, description="The ID of the company to retrieve"),
    db: Session = Depends(get_db)
):
    company = db.query(DBCompany).filter(DBCompany.id == company_id).first()
    if not company:
        raise CompanyNotFoundError(company_id)
    return company

@router.post("/", response_model=Company, status_code=201, summary="Create a new company")
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    existing_company = db.query(DBCompany).filter(DBCompany.symbol == company.symbol).first()
    if existing_company:
        raise HTTPException(status_code=400, detail=f"Company with symbol {company.symbol} already exists")
    
    db_company = DBCompany(
        name=company.name,
        symbol=company.symbol,
        sector=company.sector,
        market_cap=company.market_cap,
        exchange=company.exchange
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

@router.put("/{company_id}", response_model=Company, summary="Update company")
async def update_company(
    company_update: CompanyUpdate,
    company_id: int = Path(..., gt=0, description="The ID of the company to update"),
    db: Session = Depends(get_db)
):
    company = db.query(DBCompany).filter(DBCompany.id == company_id).first()
    if not company:
        raise CompanyNotFoundError(company_id)
    
    if company_update.symbol and company_update.symbol != company.symbol:
        existing_company = db.query(DBCompany).filter(DBCompany.symbol == company_update.symbol).first()
        if existing_company:
            raise HTTPException(status_code=400, detail=f"Company with symbol {company_update.symbol} already exists")
    
    update_data = company_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(company, field, value)
    
    db.commit()
    db.refresh(company)
    return company

@router.delete("/{company_id}", response_model=SuccessResponse, summary="Delete company")
async def delete_company(
    company_id: int = Path(..., gt=0, description="The ID of the company to delete"),
    db: Session = Depends(get_db)
):
    company = db.query(DBCompany).filter(DBCompany.id == company_id).first()
    if not company:
        raise CompanyNotFoundError(company_id)
    
    company_name = company.name
    db.delete(company)
    db.commit()
    
    return SuccessResponse(
        message=f"Company '{company_name}' deleted successfully",
        data={"deleted_company_id": company_id}
    )

@router.get("/sectors/", response_model=List[str], summary="Get all sectors")
async def get_sectors(db: Session = Depends(get_db)):
    sectors = db.query(DBCompany.sector).filter(DBCompany.sector.isnot(None)).distinct().all()
    return sorted([sector[0] for sector in sectors if sector[0]])

@router.get("/search/", response_model=List[Company], summary="Search companies by name or symbol")
async def search_companies(
    q: str = Query(..., min_length=1, description="Search query for company name or symbol"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    companies = db.query(DBCompany).filter(
        (DBCompany.name.ilike(f"%{q}%")) | (DBCompany.symbol.ilike(f"%{q}%"))
    ).limit(limit).all()
    return companies

@router.patch("/{company_id}/status", response_model=Company, summary="Toggle company active status")
async def toggle_company_status(
    company_id: int = Path(..., gt=0, description="The ID of the company"),
    db: Session = Depends(get_db)
):
    company = db.query(DBCompany).filter(DBCompany.id == company_id).first()
    if not company:
        raise CompanyNotFoundError(company_id)
    
    company.is_active = not company.is_active
    db.commit()
    db.refresh(company)
    return company