from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.scoring import calculate_vendor_risk_score

router = APIRouter(
    prefix="/scoring",
    tags=["scoring"]
)

@router.get("/vendor/{company_id}")
def get_vendor_risk_score(company_id: int, db: Session = Depends(get_db)):
    score = calculate_vendor_risk_score(company_id, db)
    if score is None:
        raise HTTPException(status_code=404, detail="No assessments found for vendor")
    return {"company_id": company_id, "risk_score": score}
