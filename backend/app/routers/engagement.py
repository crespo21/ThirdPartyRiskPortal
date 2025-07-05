from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/engagements",
    tags=["Engagements"],
)

# Error messages
ENGAGEMENT_NOT_FOUND = "Engagement not found"

@router.post("/", response_model=schemas.EngagementResponse)
def create_engagement(engagement: schemas.EngagementCreate, db: Session = Depends(get_db)):
    db_engagement = models.Engagement(**engagement.dict())
    db.add(db_engagement)
    db.commit()
    db.refresh(db_engagement)
    return db_engagement

@router.get("/", response_model=List[schemas.EngagementResponse])
def read_engagements(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    engagements = db.query(models.Engagement).offset(skip).limit(limit).all()
    return engagements

@router.get("/{engagement_id}", response_model=schemas.EngagementResponse)
def read_engagement(engagement_id: int, db: Session = Depends(get_db)):
    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if engagement is None:
        raise HTTPException(status_code=404, detail=ENGAGEMENT_NOT_FOUND)
    return engagement

@router.put("/{engagement_id}", response_model=schemas.EngagementResponse)
def update_engagement(engagement_id: int, engagement: schemas.EngagementUpdate, db: Session = Depends(get_db)):
    db_engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if db_engagement is None:
        raise HTTPException(status_code=404, detail=ENGAGEMENT_NOT_FOUND)
    update_data = engagement.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_engagement, key, value)
    db.commit()
    db.refresh(db_engagement)
    return db_engagement

@router.delete("/{engagement_id}", response_model=schemas.EngagementResponse)
def delete_engagement(engagement_id: int, db: Session = Depends(get_db)):
    db_engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if db_engagement is None:
        raise HTTPException(status_code=404, detail=ENGAGEMENT_NOT_FOUND)
    db.delete(db_engagement)
    db.commit()
    return db_engagement