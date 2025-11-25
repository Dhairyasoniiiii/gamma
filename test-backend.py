"""
Test script to verify backend is working
"""
import sys
sys.path.insert(0, '.')

print("Testing backend imports...")

try:
    from backend.config import settings
    print("✅ Config loaded")
    
    from backend.db.base import init_db, Base, engine
    print("✅ Database module loaded")
    
    from backend.models.user import User
    print("✅ User model loaded")
    
    from backend.models.presentation import Presentation
    print("✅ Presentation model loaded")
    
    from backend.models.template import Template
    print("✅ Template model loaded")
    
    from backend.models.theme import Theme
    print("✅ Theme model loaded")
    
    from backend.models.workspace import Workspace
    print("✅ Workspace model loaded")
    
    from backend.main import app
    print("✅ FastAPI app loaded")
    
    # Try to create tables
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    print("\n🎉 ALL TESTS PASSED!")
    print(f"\nDatabase: {settings.DATABASE_URL}")
    print("Backend is ready to run!")
    print("\nStart the server with:")
    print("  .\\start-backend.ps1")
    print("\nOr manually:")
    print('  $env:PYTHONPATH="C:\\Users\\PC\\OneDrive\\Desktop\\gamma clone"')
    print('  C:/Python39/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000')
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
