from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DueDiligenceRequest
from ..schemas import (DueDiligenceCreate, DueDiligenceResponse,
                       DueDiligenceUpdate)

router = APIRouter(
    prefix="/due_diligence",
    tags=["due_diligence"]
)

@router.post("/", response_model=DueDiligenceResponse)
def create_due_diligence_request(dd_data: DueDiligenceCreate, db: Session = Depends(get_db)):
    """Create a new due diligence request"""
    dd_dict = dd_data.model_dump()
    dd_dict['request_date'] = datetime.now(timezone.utc)
    
    request = DueDiligenceRequest(**dd_dict)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

@router.get("/{request_id}", response_model=DueDiligenceResponse)
def get_due_diligence_request(request_id: int, db: Session = Depends(get_db)):
    """Get a due diligence request by ID"""
    request = db.query(DueDiligenceRequest).filter(DueDiligenceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Due diligence request not found")
    return request

@router.get("/", response_model=List[DueDiligenceResponse])
def get_due_diligence_requests(db: Session = Depends(get_db)):
    """Get all due diligence requests"""
    return db.query(DueDiligenceRequest).all()

@router.put("/{request_id}", response_model=DueDiligenceResponse)
def update_due_diligence_request(request_id: int, dd_data: DueDiligenceUpdate, db: Session = Depends(get_db)):
    """Update a due diligence request"""
    request = db.query(DueDiligenceRequest).filter(DueDiligenceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Due diligence request not found")
    
    update_data = dd_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)
    
    db.commit()
    db.refresh(request)
    return request

@router.delete("/{request_id}")
def delete_due_diligence_request(request_id: int, db: Session = Depends(get_db)):
    """Delete a due diligence request"""
    request = db.query(DueDiligenceRequest).filter(DueDiligenceRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Due diligence request not found")
    
    db.delete(request)
    db.commit()
    return {"message": "Due diligence request deleted successfully"}
