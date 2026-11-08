"""
Create admin_promotions table in PostgreSQL
Run: python create_admin_table.py
"""

from backend.database import engine
from backend.models.admin_promotion import AdminPromotion

def create_table():
    try:
        print("🔄 Creating admin_promotions table...")
        AdminPromotion.__table__.create(engine, checkfirst=True)
        print("✅ admin_promotions table created successfully!")
        
        # Verify
        from backend.database import SessionLocal
        db = SessionLocal()
        result = db.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'admin_promotions')")
        exists = result.fetchone()[0]
        if exists:
            print("✅ Table verified! It exists in the database.")
        else:
            print("❌ Table not found! Something went wrong.")
        db.close()
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_table()