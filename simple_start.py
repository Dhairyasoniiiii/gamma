"""Simple server starter"""
import os
import sys

os.environ['PYTHONPATH'] = r'C:\Users\PC\OneDrive\Desktop\gamma clone'
sys.path.insert(0, r'C:\Users\PC\OneDrive\Desktop\gamma clone')

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
