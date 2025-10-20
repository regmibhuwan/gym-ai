#!/usr/bin/env python3
"""
GymAI Frontend Startup Script
This script starts the Streamlit frontend server
"""

import os
import sys
import subprocess

# Add the frontend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'frontend'))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8501))
    
    # Start Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])

