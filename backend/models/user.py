from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, Text, Float
from sqlalchemy.sql import func
import sys
import os

# Add parent directory to path if running from backend folder
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from backend.database import Base
except ImportError:
    from database import Base

class User(Base):
    __tablename__ = "users"
    
    # ============================================================
    # BASIC FIELDS
    # ============================================================
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default="HR")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # ============================================================
    # PERSONAL INFORMATION
    # ============================================================
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    linkedin = Column(String(200), nullable=True)
    github = Column(String(200), nullable=True)
    
    # ============================================================
    # EMPLOYMENT DETAILS
    # ============================================================
    designation = Column(String(100), nullable=True)
    department = Column(String(50), nullable=True)
    joining_date = Column(Date, nullable=True)
    
    # ============================================================
    # PROMOTION FIELDS
    # ============================================================
    previous_designation = Column(String(100), nullable=True)
    promotion_date = Column(Date, nullable=True)
    promotion_reason = Column(Text, nullable=True)
    salary_increment = Column(String(20), nullable=True)
    promotion_count = Column(Integer, default=0)
    
    # ============================================================
    # EDUCATION FIELDS
    # ============================================================
    education_matric = Column(String(200), nullable=True)
    education_inter = Column(String(200), nullable=True)
    education_bachelor = Column(String(200), nullable=True)
    education_master = Column(String(200), nullable=True)
    education_phd = Column(String(200), nullable=True)
    
    # ============================================================
    # SKILLS
    # ============================================================
    skills = Column(String(500), nullable=True)
    
    # ============================================================
    # ADDITIONAL INFO
    # ============================================================
    profile_picture = Column(String(255), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # ============================================================
    # SALARY & COMPENSATION
    # ============================================================
    basic_salary = Column(Float, nullable=True)
    total_salary = Column(Float, nullable=True)
    last_salary_revision = Column(Date, nullable=True)
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.full_name
    
    def get_designation_display(self):
        return self.designation if self.designation else "HR Staff"
    
    def get_education_dict(self):
        return {
            "matric": self.education_matric or "",
            "inter": self.education_inter or "",
            "bachelor": self.education_bachelor or "",
            "master": self.education_master or "",
            "phd": self.education_phd or ""
        }
    
    def get_skills_list(self):
        if self.skills:
            return [s.strip() for s in self.skills.split(',') if s.strip()]
        return []
    
    def is_promoted(self):
        return self.promotion_date is not None
    
    def get_promotion_info(self):
        if self.is_promoted():
            return {
                "from": self.previous_designation or "N/A",
                "to": self.designation,
                "date": self.promotion_date.strftime("%Y-%m-%d") if self.promotion_date else "N/A",
                "reason": self.promotion_reason or "N/A",
                "increment": self.salary_increment or "N/A",
                "count": self.promotion_count or 0
            }
        return None
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "is_active": self.is_active,
            "designation": self.designation,
            "department": self.department,
            "joining_date": self.joining_date.strftime("%Y-%m-%d") if self.joining_date else None,
            "phone": self.phone,
            "city": self.city,
            "linkedin": self.linkedin,
            "github": self.github,
            "education": self.get_education_dict(),
            "skills": self.get_skills_list(),
            "promotion_info": self.get_promotion_info(),
            "basic_salary": self.basic_salary,
            "total_salary": self.total_salary,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }