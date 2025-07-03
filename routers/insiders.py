from typing import List, Optional
from fastapi import APIRouter, Query, Path, HTTPException, Depends
from sqlalchemy.orm import Session
from models.schemas import Insider, InsiderCreate, InsiderUpdate, SuccessResponse, PaginatedResponse
from models.database_models import Insider as DBInsider, Company as DBCompany
from utils.exceptions import InsiderNotFoundError, CompanyNotFoundError
from database import get_db

router = APIRouter(prefix="/insiders", tags=["insiders"])


@router.get("/", response_model=PaginatedResponse, summary="Get all insiders")
async def get_insiders(
    skip: int = Query(0, ge=0, description="Number of insiders to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of insiders to return"),
    active_only: bool = Query(False, description="Filter active insiders only"),
    db: Session = Depends(get_db)
):
    query = db.query(DBInsider)
    if active_only:
        query = query.filter(DBInsider.is_active == True)
    
    total = query.count()
    insiders = query.offset(skip).limit(limit).all()
    
    return PaginatedResponse(
        items=[{"id": i.id, "name": i.name, "title": i.title, "company_id": i.company_id, "created_at": i.created_at, "is_active": i.is_active} for i in insiders],
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{insider_id}", response_model=Insider, summary="Get insider by ID")
async def get_insider(
    insider_id: int = Path(..., gt=0, description="The ID of the insider to retrieve"),
    db: Session = Depends(get_db)
):
    insider = db.query(DBInsider).filter(DBInsider.id == insider_id).first()
    if not insider:
        raise InsiderNotFoundError(insider_id)
    return insider

@router.post("/", response_model=Insider, status_code=201, summary="Create a new insider")
async def create_insider(insider: InsiderCreate, db: Session = Depends(get_db)):
    company = db.query(DBCompany).filter(DBCompany.id == insider.company_id).first()
    if not company:
        raise CompanyNotFoundError(insider.company_id)
    
    db_insider = DBInsider(
        name=insider.name,
        title=insider.title,
        company_id=insider.company_id
    )
    db.add(db_insider)
    db.commit()
    db.refresh(db_insider)
    return db_insider

@router.put("/{insider_id}", response_model=Insider, summary="Update insider")
async def update_insider(
    insider_update: InsiderUpdate,
    insider_id: int = Path(..., gt=0, description="The ID of the insider to update"),
    db: Session = Depends(get_db)
):
    insider = db.query(DBInsider).filter(DBInsider.id == insider_id).first()
    if not insider:
        raise InsiderNotFoundError(insider_id)
    
    if insider_update.company_id:
        company = db.query(DBCompany).filter(DBCompany.id == insider_update.company_id).first()
        if not company:
            raise CompanyNotFoundError(insider_update.company_id)
    
    update_data = insider_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(insider, field, value)
    
    db.commit()
    db.refresh(insider)
    return insider

@router.delete("/{insider_id}", response_model=SuccessResponse, summary="Delete insider")
async def delete_insider(
    insider_id: int = Path(..., gt=0, description="The ID of the insider to delete"),
    db: Session = Depends(get_db)
):
    insider = db.query(DBInsider).filter(DBInsider.id == insider_id).first()
    if not insider:
        raise InsiderNotFoundError(insider_id)
    
    insider_name = insider.name
    db.delete(insider)
    db.commit()
    
    return SuccessResponse(
        message=f"Insider {insider_name} deleted successfully",
        data={"deleted_insider_id": insider_id}
    )

@router.get("/search/", response_model=List[Insider], summary="Search insiders by name")
async def search_insiders(
    q: str = Query(..., min_length=1, description="Search query for insider name"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    insiders = db.query(DBInsider).filter(
        DBInsider.name.ilike(f"%{q}%")
    ).limit(limit).all()
    return insiders

@router.get("/company/{company_id}", response_model=List[Insider], summary="Get insiders by company")
async def get_insiders_by_company(
    company_id: int = Path(..., gt=0, description="The ID of the company"),
    active_only: bool = Query(False, description="Show only active insiders"),
    db: Session = Depends(get_db)
):
    company = db.query(DBCompany).filter(DBCompany.id == company_id).first()
    if not company:
        raise CompanyNotFoundError(company_id)
    
    query = db.query(DBInsider).filter(DBInsider.company_id == company_id)
    if active_only:
        query = query.filter(DBInsider.is_active == True)
    
    return query.all()