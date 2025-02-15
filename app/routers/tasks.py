from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Task

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("/")
def create_task(task_description: str, assigned_to: str, due_date: str, status: str, company_id: int, db: Session = Depends(get_db)):
    due_dt = datetime.fromisoformat(due_date)
    task = Task(task_description=task_description, assigned_to=assigned_to, due_date=due_dt, status=status, company_id=company_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()
