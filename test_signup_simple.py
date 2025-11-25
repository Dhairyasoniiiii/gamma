"""Simple signup test"""
import sys
sys.path.insert(0, r'C:\Users\PC\OneDrive\Desktop\gamma clone')

from backend.db.base import SessionLocal, init_db
from backend.models.user import User
from backend.utils.auth import get_password_hash

# Initialize database
print("Initializing database...")
init_db()

# Create session
db = SessionLocal()

try:
    # Check if user exists
    existing = db.query(User).filter(User.email == "simple@test.com").first()
    if existing:
        print(f"User already exists: {existing.email}")
        db.delete(existing)
        db.commit()
        print("Deleted existing user")
    
    # Create new user
    print("\nCreating new user...")
    hashed_pw = get_password_hash("password123")
    
    new_user = User(
        email="simple@test.com",
        password_hash=hashed_pw,
        name="Simple Test",
        plan='free',
        credits_remaining=400
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"✅ User created successfully!")
    print(f"   ID: {new_user.id}")
    print(f"   Email: {new_user.email}")
    print(f"   Name: {new_user.name}")
    print(f"   Credits: {new_user.credits_remaining}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
