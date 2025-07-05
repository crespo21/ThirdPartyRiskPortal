from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator
from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


# SQLAlchemy Models
class Company(Base):
    __tablename__ = "core_company"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    industry = Column(String(100))
    country = Column(String(100))
    risk_tier = Column(String(50), default="MEDIUM")
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    assessments = relationship("ThirdPartyRiskAssessment", back_populates="company", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="company", cascade="all, delete-orphan")
    due_diligence_requests = relationship("DueDiligenceRequest", back_populates="company", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="company", cascade="all, delete-orphan")
    contacts = relationship("CompanyContact", back_populates="company", cascade="all, delete-orphan")

class CompanyContact(Base):
    __tablename__ = "company_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("core_company.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    role = Column(String(100))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    company = relationship("Company", back_populates="contacts")

class Engagement(Base):
    __tablename__ = "sn_vdr_engagement"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), default="ACTIVE")
    company_id = Column(Integer, ForeignKey("core_company.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    company = relationship("Company")

class ThirdPartyRiskAssessment(Base):
    __tablename__ = "sn_vdr_risk_asmt_assessment"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_score = Column(Float)
    risk_level = Column(String(50))
    assessment_type = Column(String(100))  # INTERNAL, EXTERNAL, TIERING
    date_assessed = Column(DateTime, default=func.now())
    next_assessment_date = Column(DateTime)
    status = Column(String(50), default="PENDING")
    company_id = Column(Integer, ForeignKey("core_company.id"), nullable=False)
    assessor_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    company = relationship("Company", back_populates="assessments")

class Task(Base):
    __tablename__ = "sn_vdr_risk_asmt_task"
    
    id = Column(Integer, primary_key=True, index=True)
    task_description = Column(Text, nullable=False)
    assigned_to = Column(String(255))
    due_date = Column(DateTime)
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, OVERDUE
    priority = Column(String(50), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    company_id = Column(Integer, ForeignKey("core_company.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("sn_vdr_risk_asmt_assessment.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    company = relationship("Company", back_populates="tasks")

class DueDiligenceRequest(Base):
    __tablename__ = "sn_tprm_dd_request"
    
    id = Column(Integer, primary_key=True, index=True)
    request_details = Column(Text, nullable=False)
    request_date = Column(DateTime, default=func.now())
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED, COMPLETED
    priority = Column(String(50), default="MEDIUM")
    due_date = Column(DateTime)
    company_id = Column(Integer, ForeignKey("core_company.id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    company = relationship("Company", back_populates="due_diligence_requests")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    blob_name = Column(String(255), nullable=False)
    content_type = Column(String(100))
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=func.now())
    company_id = Column(Integer, ForeignKey("core_company.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    document_type = Column(String(100))  # CONTRACT, ASSESSMENT, COMPLIANCE, etc.
    status = Column(String(50), default="ACTIVE")
    metadata = Column(JSON)  # Additional metadata as JSON
    
    company = relationship("Company", back_populates="documents")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="USER")  # ADMIN, ASSESSOR, APPROVER, USER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)
    
    # Relationships
    assessments = relationship("ThirdPartyRiskAssessment", foreign_keys="ThirdPartyRiskAssessment.assessor_id")
    due_diligence_requests = relationship("DueDiligenceRequest", foreign_keys="DueDiligenceRequest.requester_id")
    assigned_due_diligence = relationship("DueDiligenceRequest", foreign_keys="DueDiligenceRequest.assigned_to")
    documents = relationship("Document", foreign_keys="Document.uploaded_by")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=func.now())

# Pydantic Models for API
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    risk_tier: str = Field("MEDIUM", regex="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    status: str = Field("ACTIVE", regex="^(ACTIVE|INACTIVE|SUSPENDED)$")

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    risk_tier: Optional[str] = Field(None, regex="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    status: Optional[str] = Field(None, regex="^(ACTIVE|INACTIVE|SUSPENDED)$")

class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

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

class AssessmentBase(BaseModel):
    risk_score: Optional[float] = Field(None, ge=0, le=100)
    risk_level: Optional[str] = Field(None, regex="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    assessment_type: str = Field(..., regex="^(INTERNAL|EXTERNAL|TIERING)$")
    next_assessment_date: Optional[datetime] = None
    notes: Optional[str] = None

class AssessmentCreate(AssessmentBase):
    company_id: int

class AssessmentUpdate(BaseModel):
    risk_score: Optional[float] = Field(None, ge=0, le=100)
    risk_level: Optional[str] = Field(None, regex="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    next_assessment_date: Optional[datetime] = None
    status: Optional[str] = Field(None, regex="^(PENDING|IN_PROGRESS|COMPLETED|CANCELLED)$")
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

class TaskBase(BaseModel):
    task_description: str = Field(..., min_length=1)
    assigned_to: Optional[str] = Field(None, max_length=255)
    due_date: Optional[datetime] = None
    priority: str = Field("MEDIUM", regex="^(LOW|MEDIUM|HIGH|CRITICAL)$")

class TaskCreate(TaskBase):
    company_id: int
    assessment_id: Optional[int] = None

class TaskUpdate(BaseModel):
    task_description: Optional[str] = Field(None, min_length=1)
    assigned_to: Optional[str] = Field(None, max_length=255)
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(None, regex="^(PENDING|IN_PROGRESS|COMPLETED|OVERDUE)$")
    priority: Optional[str] = Field(None, regex="^(LOW|MEDIUM|HIGH|CRITICAL)$")

class TaskResponse(TaskBase):
    id: int
    company_id: int
    assessment_id: Optional[int]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DueDiligenceBase(BaseModel):
    request_details: str = Field(..., min_length=1)
    priority: str = Field("MEDIUM", regex="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    due_date: Optional[datetime] = None

class DueDiligenceCreate(DueDiligenceBase):
    company_id: int

class DueDiligenceUpdate(BaseModel):
    request_details: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, regex="^(PENDING|APPROVED|REJECTED|COMPLETED)$")
    priority: Optional[str] = Field(None, regex="^(LOW|MEDIUM|HIGH|CRITICAL)$")
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

class DocumentBase(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    original_name: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(..., max_length=100)
    file_size: int = Field(..., gt=0)
    document_type: str = Field(..., regex="^(CONTRACT|ASSESSMENT|COMPLIANCE|FINANCIAL|OTHER)$")

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
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: str = Field(..., max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    role: str = Field("USER", regex="^(ADMIN|ASSESSOR|APPROVER|USER)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, max_length=255)
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, regex="^(ADMIN|ASSESSOR|APPROVER|USER)$")
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None