from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Company

router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)

@router.post("/")
def create_company(name: str, db: Session = Depends(get_db)):
    existing = db.query(Company).filter(Company.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company already exists")
    new_company = Company(name=name)
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company

@router.get("/{company_id}")
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.get("/")
def get_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()
