from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import DueDiligenceRequest

router = APIRouter(
    prefix="/due_diligence",
    tags=["due_diligence"]
)

@router.post("/")
def create_due_diligence_request(company_id: int, request_details: str, db: Session = Depends(get_db)):
    request = DueDiligenceRequest(company_id=company_id, request_details=request_details, request_date=datetime.utcnow())
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

@router.get("/{request_id}")
def get_due_diligence_request(request_id: int, db: Session = Depends(get_db)):
    request = db.query(DueDiligenceRequest).filter(DueDiligenceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Due diligence request not found")
    return request

@router.get("/")
def get_due_diligence_requests(db: Session = Depends(get_db)):
    return db.query(DueDiligenceRequest).all()
