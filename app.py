# Move main.py to root for Render deployment
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the app from backend
from backend.main import app

# This allows Render to find the app
__all__ = ['app']
