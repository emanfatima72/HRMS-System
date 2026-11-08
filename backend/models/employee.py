from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from backend.database import Base
except ImportError:
    from database import Base

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    emp_id = Column(String(50), unique=True, nullable=True)
    name = Column(String(100), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(String(255))
    city = Column(String(100))
    linkedin = Column(String(255))
    github = Column(String(255))
    dob = Column(String(20))
    
    education = Column(JSON, default={})
    skills = Column(JSON, default=[])
    
    cv_path = Column(String(500))
    photo1 = Column(String(500))
    photo2 = Column(String(500))
    criminal_letter = Column(String(500))
    additional_docs = Column(JSON, default=[])
    
    designation = Column(String(100))
    department = Column(String(100))
    employee_type = Column(String(50))
    salary = Column(Integer, default=0)
    joining_date = Column(Date)
    active_days = Column(Integer, default=0)
    extra_work = Column(Integer, default=0)
    
    status = Column(String(20), default="Pending")
    
    exit_type = Column(String(50))
    exit_date = Column(Date)
    exit_reason = Column(Text)
    
    reject_reason = Column(Text)
    rejected_on = Column(DateTime)
    
    submitted_on = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # ===== RELATIONSHIPS =====
    attendances = relationship("Attendance", back_populates="employee")
    leaves = relationship("Leave", back_populates="employee")
    promotion_records = relationship("Promotion", back_populates="employee")
    admin_promotions = relationship("AdminPromotion", back_populates="employee")