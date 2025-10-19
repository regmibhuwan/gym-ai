#!/usr/bin/env python3
"""
GymAI Backend Startup Script
This script starts the FastAPI backend server
"""

import os
import sys
import uvicorn

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
