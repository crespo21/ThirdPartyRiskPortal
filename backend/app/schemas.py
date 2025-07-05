"""
Pydantic schemas for API request/response models.
This module contains all the Pydantic models used for API validation,
serialization, and documentation. Keep this separate from SQLAlchemy ORM models.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# Constants for validation patterns
RISK_TIER_PATTERN = "^(LOW|MEDIUM|HIGH|CRITICAL)$"

# Company Schemas
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    risk_tier: str = Field("MEDIUM", pattern=RISK_TIER_PATTERN)
    status: str = Field("ACTIVE", pattern="^(ACTIVE|INACTIVE|SUSPENDED)$")

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    risk_tier: Optional[str] = Field(None, pattern=RISK_TIER_PATTERN)
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE|SUSPENDED)$")

class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Company Contact Schemas
class CompanyContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100)
    is_primary: bool = False

class CompanyContactCreate(CompanyContactBase):
    company_id: int

class CompanyContactResponse(CompanyContactBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Engagement Schemas
class EngagementBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = Field("ACTIVE", pattern="^(ACTIVE|INACTIVE|COMPLETED|CANCELLED)$")

class EngagementCreate(EngagementBase):
    company_id: int

class EngagementUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(ACTIVE|INACTIVE|COMPLETED|CANCELLED)$")

class EngagementResponse(EngagementBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Assessment Schemas
class AssessmentBase(BaseModel):
    risk_score: Optional[float] = Field(None, ge=0, le=100)
    risk_level: Optional[str] = Field(None, pattern=RISK_TIER_PATTERN)
    assessment_type: str = Field(..., pattern="^(INTERNAL|EXTERNAL|TIERING)$")
    next_assessment_date: Optional[datetime] = None
    notes: Optional[str] = None

class AssessmentCreate(AssessmentBase):
    company_id: int

class AssessmentUpdate(BaseModel):
    risk_score: Optional[float] = Field(None, ge=0, le=100)
    risk_level: Optional[str] = Field(None, pattern=RISK_TIER_PATTERN)
    next_assessment_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(PENDING|IN_PROGRESS|COMPLETED|CANCELLED)$")
    notes: Optional[str] = None

class AssessmentResponse(AssessmentBase):
    id: int
    company_id: int
    date_assessed: datetime
    status: str
    assessor_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    task_description: str = Field(..., min_length=1)
    assigned_to: Optional[str] = Field(None, max_length=255)
    due_date: Optional[datetime] = None
    priority: str = Field("MEDIUM", pattern=RISK_TIER_PATTERN)

class TaskCreate(TaskBase):
    company_id: int
    assessment_id: Optional[int] = None

class TaskUpdate(BaseModel):
    task_description: Optional[str] = Field(None, min_length=1)
    assigned_to: Optional[str] = Field(None, max_length=255)
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(PENDING|IN_PROGRESS|COMPLETED|OVERDUE)$")
    priority: Optional[str] = Field(None, pattern=RISK_TIER_PATTERN)

class TaskResponse(TaskBase):
    id: int
    company_id: int
    assessment_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Due Diligence Schemas
class DueDiligenceBase(BaseModel):
    request_details: str = Field(..., min_length=1)
    priority: str = Field("MEDIUM", pattern=RISK_TIER_PATTERN)
    due_date: Optional[datetime] = None

class DueDiligenceCreate(DueDiligenceBase):
    company_id: int

class DueDiligenceUpdate(BaseModel):
    request_details: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern="^(PENDING|APPROVED|REJECTED|COMPLETED)$")
    priority: Optional[str] = Field(None, pattern=RISK_TIER_PATTERN)
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None

class DueDiligenceResponse(DueDiligenceBase):
    id: int
    company_id: int
    request_date: datetime
    status: str
    requester_id: Optional[int]
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Document Schemas
class DocumentBase(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    original_name: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., max_length=100)
    file_size: int = Field(..., gt=0)
    document_type: str = Field(..., pattern="^(CONTRACT|ASSESSMENT|COMPLIANCE|FINANCIAL|OTHER)$")

class DocumentCreate(DocumentBase):
    company_id: int
    blob_name: str

class DocumentResponse(DocumentBase):
    id: int
    company_id: int
    blob_name: str
    upload_date: datetime
    uploaded_by: Optional[int]
    status: str
    document_metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: str = Field(..., max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    role: str = Field("USER", pattern="^(ADMIN|ASSESSOR|APPROVER|USER)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, pattern="^(ADMIN|ASSESSOR|APPROVER|USER)$")
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
