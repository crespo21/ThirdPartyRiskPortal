from sqlalchemy.orm import Session
from ..models import ThirdPartyRiskAssessment

def calculate_vendor_risk_score(company_id: int, db: Session):
    assessments = db.query(ThirdPartyRiskAssessment).filter(
        ThirdPartyRiskAssessment.company_id == company_id
    ).all()
    if not assessments:
        return None
    total_score = sum([assessment.risk_score for assessment in assessments])
    avg_score = total_score / len(assessments)
    return avg_score
