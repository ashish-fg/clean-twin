"""API endpoints for inspection management."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models.inspection import InspectionStatus
from ..services.inspection_service import InspectionService
from .deps import get_db


# Pydantic models for request/response validation

class InspectionCreate(BaseModel):
    """Request model for creating a new inspection."""
    building_name: str = Field(..., min_length=1, max_length=200, description="Name of the building")
    building_address: str = Field(..., min_length=1, description="Address of the building")
    operator_name: str = Field(..., min_length=1, max_length=100, description="Name of the operator")
    total_area_sqm: float = Field(..., gt=0, description="Total area in square meters (must be positive)")

    @field_validator('building_name', 'building_address', 'operator_name')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that string fields are not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or just whitespace")
        return v.strip()


class InspectionStatusUpdate(BaseModel):
    """Request model for updating inspection status."""
    status: str = Field(..., description="New status value")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is a valid enum value."""
        try:
            InspectionStatus(v)
        except ValueError:
            valid_values = [s.value for s in InspectionStatus]
            raise ValueError(f"Invalid status. Must be one of: {valid_values}")
        return v


class InspectionScoreUpdate(BaseModel):
    """Request model for updating inspection quality score."""
    score: float = Field(..., ge=0, le=100, description="Quality score between 0 and 100")


class InspectionResponse(BaseModel):
    """Response model for inspection data."""
    id: UUID
    building_name: str
    building_address: str
    inspection_date: datetime
    operator_name: str
    status: str
    overall_quality_score: Optional[float]
    total_area_sqm: float
    video_path: Optional[str]
    report_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_validator('status', mode='before')
    @classmethod
    def convert_status_enum(cls, v):
        """Convert InspectionStatus enum to string value."""
        if isinstance(v, InspectionStatus):
            return v.value
        return v


# API Router

router = APIRouter(prefix="/inspections", tags=["inspections"])


@router.post(
    "",
    response_model=InspectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new inspection",
    description="Create a new building inspection with the provided details"
)
def create_inspection(
    inspection_data: InspectionCreate,
    db: Session = Depends(get_db)
) -> InspectionResponse:
    """
    Create a new inspection.

    Args:
        inspection_data: Inspection creation data
        db: Database session (injected)

    Returns:
        Created inspection details

    Raises:
        HTTPException 400: If validation fails
        HTTPException 500: If database error occurs
    """
    service = InspectionService()
    try:
        inspection = service.create_inspection(
            building_name=inspection_data.building_name,
            building_address=inspection_data.building_address,
            operator_name=inspection_data.operator_name,
            total_area_sqm=inspection_data.total_area_sqm
        )
        return InspectionResponse.model_validate(inspection)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get(
    "/{inspection_id}",
    response_model=InspectionResponse,
    summary="Get inspection by ID",
    description="Retrieve details of a specific inspection by its UUID"
)
def get_inspection(
    inspection_id: UUID,
    db: Session = Depends(get_db)
) -> InspectionResponse:
    """
    Get inspection by ID.

    Args:
        inspection_id: UUID of the inspection
        db: Database session (injected)

    Returns:
        Inspection details

    Raises:
        HTTPException 404: If inspection not found
        HTTPException 500: If database error occurs
    """
    service = InspectionService()
    try:
        inspection = service.get_inspection(inspection_id)
        if inspection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inspection with id {inspection_id} not found"
            )
        return InspectionResponse.model_validate(inspection)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.get(
    "",
    response_model=List[InspectionResponse],
    summary="List inspections",
    description="Get a paginated list of inspections ordered by creation date (newest first)"
)
def list_inspections(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[InspectionResponse]:
    """
    List inspections with pagination.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100)
        db: Database session (injected)

    Returns:
        List of inspections (empty list if no inspections found)

    Raises:
        HTTPException 500: If database error occurs
    """
    service = InspectionService()
    try:
        inspections = service.list_inspections(skip=skip, limit=limit)
        return [InspectionResponse.model_validate(insp) for insp in inspections]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.patch(
    "/{inspection_id}/status",
    response_model=InspectionResponse,
    summary="Update inspection status",
    description="Update the status of an inspection (pending, in_progress, completed, failed)"
)
def update_inspection_status(
    inspection_id: UUID,
    status_data: InspectionStatusUpdate,
    db: Session = Depends(get_db)
) -> InspectionResponse:
    """
    Update inspection status.

    Args:
        inspection_id: UUID of the inspection
        status_data: New status data
        db: Database session (injected)

    Returns:
        Updated inspection details

    Raises:
        HTTPException 404: If inspection not found
        HTTPException 400: If status value is invalid
        HTTPException 500: If database error occurs
    """
    service = InspectionService()
    try:
        inspection = service.update_inspection_status(
            inspection_id=inspection_id,
            status=status_data.status
        )
        if inspection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inspection with id {inspection_id} not found"
            )
        return InspectionResponse.model_validate(inspection)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@router.patch(
    "/{inspection_id}/score",
    response_model=InspectionResponse,
    summary="Update inspection quality score",
    description="Update the overall quality score of an inspection (0-100)"
)
def update_inspection_score(
    inspection_id: UUID,
    score_data: InspectionScoreUpdate,
    db: Session = Depends(get_db)
) -> InspectionResponse:
    """
    Update inspection quality score.

    Args:
        inspection_id: UUID of the inspection
        score_data: New score data
        db: Database session (injected)

    Returns:
        Updated inspection details

    Raises:
        HTTPException 404: If inspection not found
        HTTPException 400: If score value is invalid
        HTTPException 500: If database error occurs
    """
    service = InspectionService()
    try:
        inspection = service.update_quality_score(
            inspection_id=inspection_id,
            score=score_data.score
        )
        if inspection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inspection with id {inspection_id} not found"
            )
        return InspectionResponse.model_validate(inspection)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
