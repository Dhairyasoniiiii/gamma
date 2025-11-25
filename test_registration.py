import sys
sys.path.insert(0, r'C:\Users\PC\OneDrive\Desktop\gamma clone')

from backend.db.base import SessionLocal
from backend.models.user import User
from backend.utils.auth import get_password_hash
from backend.config import settings
import traceback

db = SessionLocal()

try:
    print("Testing user registration...")
    
    # Check if user exists
    existing = db.query(User).filter(User.email == "test@example.com").first()
    if existing:
        print(f"User exists, deleting: {existing.id}")
        db.delete(existing)
        db.commit()
    
    # Create new user
    print("\nHashing password...")
    hashed_password = get_password_hash("password123")
    print(f"Password hash created: {hashed_password[:30]}...")
    
    print("\nCreating user object...")
    new_user = User(
        email="test@example.com",
        password_hash=hashed_password,
        name="Test User",
        plan='free',
        credits_remaining=settings.CREDITS_FREE_PLAN
    )
    
    print(f"User object created with ID: {new_user.id}")
    print(f"Email: {new_user.email}")
    print(f"Name: {new_user.name}")
    print(f"Plan: {new_user.plan}")
    print(f"Credits: {new_user.credits_remaining}")
    
    print("\nAdding to database...")
    db.add(new_user)
    
    print("Committing...")
    db.commit()
    
    print("Refreshing...")
    db.refresh(new_user)
    
    print(f"\n✅ SUCCESS! User created with ID: {new_user.id}")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
