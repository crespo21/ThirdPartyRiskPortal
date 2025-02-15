from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Company(Base):
    __tablename__ = "core_company"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    # Relationships
    assessments = relationship("ThirdPartyRiskAssessment", back_populates="company")
    tasks = relationship("Task", back_populates="company")
    due_diligence_requests = relationship("DueDiligenceRequest", back_populates="company")

class ThirdPartyRiskAssessment(Base):
    __tablename__ = "sn_vdr_risk_asmt_assessment"
    id = Column(Integer, primary_key=True, index=True)
    risk_score = Column(Float)
    date_assessed = Column(DateTime)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    company = relationship("Company", back_populates="assessments")

class Task(Base):
    __tablename__ = "sn_vdr_risk_asmt_task"
    id = Column(Integer, primary_key=True, index=True)
    task_description = Column(Text)
    assigned_to = Column(String)
    due_date = Column(DateTime)
    status = Column(String)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    company = relationship("Company", back_populates="tasks")

class DueDiligenceRequest(Base):
    __tablename__ = "sn_tprm_dd_request"
    id = Column(Integer, primary_key=True, index=True)
    request_details = Column(Text)
    request_date = Column(DateTime)
    company_id = Column(Integer, ForeignKey("core_company.id"))
    company = relationship("Company", back_populates="due_diligence_requests")
