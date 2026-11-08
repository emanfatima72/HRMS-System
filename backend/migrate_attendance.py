# backend/migrate_attendance.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import engine
from sqlalchemy import text

def migrate_attendance():
    with engine.connect() as conn:
        # Check if employee_id column exists
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='attendance' AND column_name='employee_id'"
        ))
        if not result.fetchone():
            conn.execute(text("ALTER TABLE attendance ADD COLUMN employee_id INTEGER REFERENCES employees(id)"))
            conn.commit()
            print('✅ employee_id column added successfully!')
        else:
            print('✅ employee_id column already exists!')

if __name__ == "__main__":
    print("🔄 Running attendance migration...")
    migrate_attendance()
    print("✅ Migration completed!")