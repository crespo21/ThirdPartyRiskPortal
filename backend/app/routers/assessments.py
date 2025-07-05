from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ThirdPartyRiskAssessment
from ..schemas import AssessmentCreate, AssessmentResponse, AssessmentUpdate

router = APIRouter(
    prefix="/assessments",
    tags=["assessments"]
)

@router.post("/", response_model=AssessmentResponse)
def create_assessment(assessment_data: AssessmentCreate, db: Session = Depends(get_db)):
    """Create a new risk assessment"""
    assessment_dict = assessment_data.model_dump()
    assessment_dict['date_assessed'] = datetime.now(timezone.utc)
    
    assessment = ThirdPartyRiskAssessment(**assessment_dict)
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """Get an assessment by ID"""
    assessment = db.query(ThirdPartyRiskAssessment).filter(ThirdPartyRiskAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

@router.get("/", response_model=List[AssessmentResponse])
def get_assessments(db: Session = Depends(get_db)):
    """Get all assessments"""
    return db.query(ThirdPartyRiskAssessment).all()

@router.put("/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(assessment_id: int, assessment_data: AssessmentUpdate, db: Session = Depends(get_db)):
    """Update an assessment"""
    assessment = db.query(ThirdPartyRiskAssessment).filter(ThirdPartyRiskAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    update_data = assessment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assessment, field, value)
    
    db.commit()
    db.refresh(assessment)
    return assessment

@router.delete("/{assessment_id}")
def delete_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """Delete an assessment"""
    assessment = db.query(ThirdPartyRiskAssessment).filter(ThirdPartyRiskAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    db.delete(assessment)
    db.commit()
    return {"message": "Assessment deleted successfully"}
