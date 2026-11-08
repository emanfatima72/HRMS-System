from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class Promotion(Base):
    __tablename__ = "promotions"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    current_designation = Column(String(100), nullable=False)
    new_designation = Column(String(100), nullable=False)
    current_salary = Column(Float, nullable=False)
    new_salary = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    recommendation_by = Column(String(100), nullable=False)
    status = Column(String(20), default="Pending")  # ← YEH LINE ADD KAREIN
    created_at = Column(DateTime, default=datetime.now)
    approved_on = Column(DateTime, nullable=True)
    
    # Relationship with Employee
    employee = relationship("Employee", back_populates="promotion_records")