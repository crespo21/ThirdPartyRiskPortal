from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import ThirdPartyRiskAssessment

router = APIRouter(
    prefix="/assessments",
    tags=["assessments"]
)

@router.post("/")
def create_assessment(company_id: int, risk_score: float, db: Session = Depends(get_db)):
    assessment = ThirdPartyRiskAssessment(company_id=company_id, risk_score=risk_score, date_assessed=datetime.utcnow())
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

@router.get("/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(ThirdPartyRiskAssessment).filter(ThirdPartyRiskAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

@router.get("/")
def get_assessments(db: Session = Depends(get_db)):
    return db.query(ThirdPartyRiskAssessment).all()
