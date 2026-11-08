# backend/migrate_emp_id.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import engine, SessionLocal
from sqlalchemy import text
import uuid

# Import model after sys.path fix
from backend.models.employee import Employee

def update_existing_employees():
    db = SessionLocal()
    employees = db.query(Employee).all()
    updated = 0
    for emp in employees:
        if not emp.emp_id:
            emp.emp_id = f"EMP-2024-{str(uuid.uuid4())[:8].upper()}"
            updated += 1
    db.commit()
    db.close()
    print(f'✅ {updated} employees updated with emp_id!')

if __name__ == "__main__":
    print("🔄 Updating existing employees with emp_id...")
    update_existing_employees()
    print("✅ Migration completed successfully!")