from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hrms_db")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    # Import all models here to register them
    from backend.models.user import User
    from backend.models.employee import Employee
    from backend.models.attendance import Attendance
    from backend.models.leave import Leave
    from backend.models.payroll import Payroll
    from backend.models.notification import Notification
    from backend.models.promotion import Promotion
    
    Base.metadata.create_all(bind=engine)