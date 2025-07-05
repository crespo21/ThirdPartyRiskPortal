from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models import Engagement
from ..database import get_db

router = APIRouter(
    prefix="/engagements",
    tags=["Engagements"],
)

# Dependency to get the database session
def get_db():
    db = get_db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_engagement(description:str, models.Engagement, db: Session = Depends(get_db)):
    db_engagement = models.Engagement(**engagement.dict())
    db.add(db_engagement)
    db.commit()
    db.refresh(db_engagement)
    return db_engagement

@router.get("/", response_model=List[models.Engagement])
def read_engagements(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    engagements = db.query(models.Engagement).offset(skip).limit(limit).all()
    return engagements

@router.get("/{engagement_id}", response_model=models.Engagement)
def read_engagement(engagement_id: int, db: Session = Depends(get_db)):
    engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if engagement is None:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return engagement

@router.put("/{engagement_id}", response_model=models.Engagement)
def update_engagement(engagement_id: int, engagement: models.EngagementCreate, db: Session = Depends(get_db)):
    db_engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if db_engagement is None:
        raise HTTPException(status_code=404, detail="Engagement not found")
    for key, value in engagement.dict().items():
        setattr(db_engagement, key, value)
    db.commit()
    db.refresh(db_engagement)
    return db_engagement

@router.delete("/{engagement_id}", response_model=models.Engagement)
def delete_engagement(engagement_id: int, db: Session = Depends(get_db)):
    db_engagement = db.query(models.Engagement).filter(models.Engagement.id == engagement_id).first()
    if db_engagement is None:
        raise HTTPException(status_code=404, detail="Engagement not found")
    db.delete(db_engagement)
    db.commit()
    return db_engagement