"""
Simple test to run uvicorn on backend.main:app
"""
import sys
import os

# Add to path
sys.path.insert(0, "C:\\Users\\PC\\OneDrive\\Desktop\\gamma clone")
os.environ['PYTHONPATH'] = "C:\\Users\\PC\\OneDrive\\Desktop\\gamma clone"

import uvicorn

if __name__ == "__main__":
    print("[INFO] Starting uvicorn manually...")
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Server crashed: {e}")
        import traceback
        traceback.print_exc()
