# backend/migrate_db.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import engine, create_tables
from sqlalchemy import text

def drop_all_tables():
    """Drop all tables"""
    tables = ['promotions', 'leaves', 'attendance', 'employees', 'notifications', 'payroll', 'users']
    with engine.connect() as conn:
        for table in tables:
            try:
                conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
                print(f'✅ Dropped: {table}')
            except Exception as e:
                print(f'⚠️ Error dropping {table}: {e}')
        conn.commit()
    print('✅ All tables dropped!')

def create_all_tables():
    """Create all tables"""
    create_tables()
    print('✅ All tables created successfully!')

def reset_database():
    """Full reset"""
    print('🔄 Resetting database...')
    drop_all_tables()
    create_all_tables()
    print('✅ Database reset completed!')

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        print('🔄 Running migration...')
        # Only drop promotions and recreate
        with engine.connect() as conn:
            try:
                conn.execute(text('DROP TABLE IF EXISTS promotions CASCADE'))
                conn.commit()
                print('✅ Promotions table dropped!')
            except Exception as e:
                print(f'⚠️ Error: {e}')
        create_tables()
        print('✅ Migration completed!')