from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..config import settings
from ..security import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # For demo purposes, we use a fixed username and password.
    if form_data.username != "admin" or form_data.password != "password":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    return {"access_token": access_token, "token_type": "bearer"}
