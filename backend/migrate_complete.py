# backend/migrate_complete.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import engine
from sqlalchemy import text
import uuid

def add_missing_columns():
    with engine.connect() as conn:
        # List of columns to add with their types
        columns = [
            ("first_name", "VARCHAR(50)"),
            ("last_name", "VARCHAR(50)"),
            ("address", "VARCHAR(255)"),
            ("city", "VARCHAR(100)"),
            ("linkedin", "VARCHAR(255)"),
            ("github", "VARCHAR(255)"),
            ("dob", "VARCHAR(20)"),
            ("education", "JSON DEFAULT '{}'"),
            ("skills", "JSON DEFAULT '[]'"),
            ("photo1", "VARCHAR(500)"),
            ("photo2", "VARCHAR(500)"),
            ("criminal_letter", "VARCHAR(500)"),
            ("additional_docs", "JSON DEFAULT '[]'"),
            ("designation", "VARCHAR(100)"),
            ("department", "VARCHAR(100)"),
            ("employee_type", "VARCHAR(50)"),
            ("salary", "INTEGER DEFAULT 0"),
            ("joining_date", "DATE"),
            ("active_days", "INTEGER DEFAULT 0"),
            ("extra_work", "INTEGER DEFAULT 0"),
            ("exit_type", "VARCHAR(50)"),
            ("exit_date", "DATE"),
            ("exit_reason", "TEXT"),
            ("reject_reason", "TEXT"),
            ("rejected_on", "TIMESTAMP"),
            ("submitted_on", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP"),
            ("emp_id", "VARCHAR(50) UNIQUE"),
        ]
        
        added = 0
        for col_name, col_type in columns:
            # Check if column exists
            result = conn.execute(text(
                f"SELECT column_name FROM information_schema.columns WHERE table_name='employees' AND column_name='{col_name}'"
            ))
            if not result.fetchone():
                try:
                    conn.execute(text(f"ALTER TABLE employees ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    print(f'✅ Added column: {col_name}')
                    added += 1
                except Exception as e:
                    print(f'❌ Failed to add {col_name}: {e}')
            else:
                print(f'⏭️ Column already exists: {col_name}')
        
        print(f'✅ {added} new columns added successfully!')

def update_existing_employees():
    from backend.database import SessionLocal
    from backend.models.employee import Employee
    
    db = SessionLocal()
    employees = db.query(Employee).all()
    updated = 0
    
    for emp in employees:
        # Update emp_id if missing
        if not emp.emp_id:
            emp.emp_id = f"EMP-2024-{str(uuid.uuid4())[:8].upper()}"
            updated += 1
        
        # Set default values for new columns if null
        if not emp.first_name and emp.name:
            name_parts = emp.name.split()
            emp.first_name = name_parts[0] if name_parts else emp.name
            emp.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
        
        if emp.education is None:
            emp.education = {}
        if emp.skills is None:
            emp.skills = []
        if emp.additional_docs is None:
            emp.additional_docs = []
        if emp.salary is None:
            emp.salary = 0
        if emp.active_days is None:
            emp.active_days = 0
        if emp.extra_work is None:
            emp.extra_work = 0
        if emp.status is None:
            emp.status = "Pending"
    
    db.commit()
    db.close()
    print(f'✅ {updated} employees updated with emp_id!')

if __name__ == "__main__":
    print("🔄 Running complete migration...")
    print("=" * 50)
    add_missing_columns()
    print("=" * 50)
    update_existing_employees()
    print("=" * 50)
    print("✅ Migration completed successfully!")