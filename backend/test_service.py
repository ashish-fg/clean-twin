# Create: backend/test_service.py
from app.services.inspection_service import InspectionService
from uuid import uuid4

service = InspectionService()

# Test create
inspection = service.create_inspection(
    building_name="Test Building",
    building_address="123 Test St, Dubai",
    operator_name="Ashish",
    total_area_sqm=500.0
)
print(f"✓ Created: {inspection.id}")

# Test retrieve
retrieved = service.get_inspection(inspection.id)
print(f"✓ Retrieved: {retrieved.building_name}")

# Test list
inspections = service.list_inspections()
print(f"✓ Listed: {len(inspections)} inspections")

# Test update status
updated = service.update_inspection_status(inspection.id, "in_progress")
print(f"✓ Updated status: {updated.status}")
