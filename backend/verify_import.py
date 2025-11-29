import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

try:
    from app.routes import patient
    print("Successfully imported app.routes.patient")
except Exception as e:
    print(f"Failed to import app.routes.patient: {e}")
