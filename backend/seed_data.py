# backend/seed_data.py
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal
from backend.models.user import User
from backend.services.auth_service import get_password_hash

def seed_users():
    db = SessionLocal()
    
    users = [
        {"username": "hr", "email": "hr@hrms.com", "password": "hr@portal1166", "full_name": "HR Manager", "role": "HR"},
        {"username": "admin", "email": "admin@hrms.com", "password": "admin@portal1166", "full_name": "System Admin", "role": "Admin"}
    ]
    
    for user_data in users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            try:
                hashed = get_password_hash(user_data["password"])
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hashed,
                    full_name=user_data["full_name"],
                    role=user_data["role"]
                )
                db.add(user)
                print(f"✅ User {user_data['username']} created!")
            except Exception as e:
                print(f"❌ Error creating {user_data['username']}: {e}")
        else:
            print(f"⏳ User {user_data['username']} already exists")
    
    db.commit()
    db.close()
    print("✅ Default users seeded!")

if __name__ == "__main__":
    seed_users()