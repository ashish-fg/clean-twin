# Create a test script: backend/test_models.py
from app.database import engine
from app.models.base import Base
from app.models.inspection import Inspection

# This should create tables without errors
Base.metadata.create_all(bind=engine)
print("✓ Models created successfully")
