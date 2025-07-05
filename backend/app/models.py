from datetime import datetime
from typing import List, Optional

from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

# Constants
CASCADE_ALL_DELETE_ORPHAN = "all, delete-orphan"
CORE_COMPANY_ID = "core_company.id"
CORE_USERS_ID = "users.id"
RISK_TIER_PATTERN = "^(LOW|MEDIUM|HIGH|CRITICAL)$"


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
    assessments = relationship("ThirdPartyRiskAssessment", back_populates="company", cascade=CASCADE_ALL_DELETE_ORPHAN)
    tasks = relationship("Task", back_populates="company", cascade=CASCADE_ALL_DELETE_ORPHAN)
    due_diligence_requests = relationship("DueDiligenceRequest", back_populates="company", cascade=CASCADE_ALL_DELETE_ORPHAN)
    documents = relationship("Document", back_populates="company", cascade=CASCADE_ALL_DELETE_ORPHAN)
    contacts = relationship("CompanyContact", back_populates="company", cascade=CASCADE_ALL_DELETE_ORPHAN)
    contacts = relationship("CompanyContact", back_populates="company", cascade=CASCADE_ALL_DELETE_ORPHAN)

class CompanyContact(Base):
    __tablename__ = "company_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey(CORE_COMPANY_ID), nullable=False)
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
    company_id = Column(Integer, ForeignKey(CORE_COMPANY_ID), nullable=False)
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
    company_id = Column(Integer, ForeignKey(CORE_COMPANY_ID), nullable=False)
    assessor_id = Column(Integer, ForeignKey(CORE_USERS_ID))
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
    company_id = Column(Integer, ForeignKey(CORE_COMPANY_ID), nullable=False)
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
    company_id = Column(Integer, ForeignKey(CORE_COMPANY_ID), nullable=False)
    requester_id = Column(Integer, ForeignKey(CORE_USERS_ID))
    assigned_to = Column(Integer, ForeignKey(CORE_USERS_ID))
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
    company_id = Column(Integer, ForeignKey(CORE_COMPANY_ID), nullable=False)
    uploaded_by = Column(Integer, ForeignKey(CORE_USERS_ID))
    document_type = Column(String(100))  # CONTRACT, ASSESSMENT, COMPLIANCE, etc.
    status = Column(String(50), default="ACTIVE")
    document_metadata = Column(JSON)  # Additional metadata as JSON
    
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
    user_id = Column(Integer, ForeignKey(CORE_USERS_ID))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=func.now())