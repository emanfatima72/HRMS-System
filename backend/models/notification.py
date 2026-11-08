from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from backend.database import Base
except ImportError:
    from database import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=True)
    send_to = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(20), default="Normal")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())