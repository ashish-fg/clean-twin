"""Service layer for inspection operations."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models.inspection import Inspection, InspectionStatus


class InspectionService:
    """Service class for managing inspection operations."""

    def create_inspection(
        self,
        building_name: str,
        building_address: str,
        operator_name: str,
        total_area_sqm: float,
        inspection_date: Optional[datetime] = None
    ) -> Inspection:
        """
        Create a new inspection in the database.

        Args:
            building_name: Name of the building being inspected
            building_address: Address of the building
            operator_name: Name of the operator performing the inspection
            total_area_sqm: Total area of the building in square meters
            inspection_date: Date of the inspection (defaults to current time if not provided)

        Returns:
            The created Inspection object

        Raises:
            ValueError: If validation fails (e.g., negative area)
            SQLAlchemyError: If database operation fails
        """
        if total_area_sqm <= 0:
            raise ValueError("total_area_sqm must be positive")

        if inspection_date is None:
            inspection_date = datetime.now(timezone.utc)

        session: Session = SessionLocal()
        try:
            inspection = Inspection(
                building_name=building_name,
                building_address=building_address,
                operator_name=operator_name,
                total_area_sqm=total_area_sqm,
                inspection_date=inspection_date,
                status=InspectionStatus.PENDING
            )
            session.add(inspection)
            session.commit()
            session.refresh(inspection)
            return inspection
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Failed to create inspection: {str(e)}") from e
        finally:
            session.close()

    def get_inspection(self, inspection_id: UUID) -> Optional[Inspection]:
        """
        Retrieve an inspection by its ID.

        Args:
            inspection_id: UUID of the inspection to retrieve

        Returns:
            The Inspection object if found, None otherwise

        Raises:
            SQLAlchemyError: If database operation fails
        """
        session: Session = SessionLocal()
        try:
            inspection = session.query(Inspection).filter(
                Inspection.id == inspection_id
            ).first()
            return inspection
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to retrieve inspection: {str(e)}") from e
        finally:
            session.close()

    def list_inspections(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Inspection]:
        """
        Retrieve a paginated list of inspections.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return

        Returns:
            List of Inspection objects ordered by created_at descending

        Raises:
            SQLAlchemyError: If database operation fails
        """
        session: Session = SessionLocal()
        try:
            inspections = session.query(Inspection).order_by(
                Inspection.created_at.desc()
            ).offset(skip).limit(limit).all()
            return inspections
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Failed to list inspections: {str(e)}") from e
        finally:
            session.close()

    def update_inspection_status(
        self,
        inspection_id: UUID,
        status: str
    ) -> Optional[Inspection]:
        """
        Update the status of an inspection.

        Args:
            inspection_id: UUID of the inspection to update
            status: New status value (must be valid InspectionStatus enum value)

        Returns:
            The updated Inspection object if found, None if inspection not found

        Raises:
            ValueError: If status is not a valid enum value
            SQLAlchemyError: If database operation fails
        """
        # Validate status is a valid enum value
        try:
            status_enum = InspectionStatus(status)
        except ValueError:
            valid_values = [s.value for s in InspectionStatus]
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: {valid_values}"
            )

        session: Session = SessionLocal()
        try:
            inspection = session.query(Inspection).filter(
                Inspection.id == inspection_id
            ).first()

            if inspection is None:
                return None

            inspection.status = status_enum
            session.commit()
            session.refresh(inspection)
            return inspection
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Failed to update inspection status: {str(e)}") from e
        finally:
            session.close()

    def update_quality_score(
        self,
        inspection_id: UUID,
        score: float
    ) -> Optional[Inspection]:
        """
        Update the overall quality score of an inspection.

        Args:
            inspection_id: UUID of the inspection to update
            score: Quality score (must be between 0 and 100)

        Returns:
            The updated Inspection object if found, None if inspection not found

        Raises:
            ValueError: If score is not between 0 and 100
            SQLAlchemyError: If database operation fails
        """
        # Validate score range
        if score < 0 or score > 100:
            raise ValueError(
                f"Quality score must be between 0 and 100, got {score}"
            )

        session: Session = SessionLocal()
        try:
            inspection = session.query(Inspection).filter(
                Inspection.id == inspection_id
            ).first()

            if inspection is None:
                return None

            inspection.overall_quality_score = score
            session.commit()
            session.refresh(inspection)
            return inspection
        except SQLAlchemyError as e:
            session.rollback()
            raise SQLAlchemyError(f"Failed to update quality score: {str(e)}") from e
        finally:
            session.close()
