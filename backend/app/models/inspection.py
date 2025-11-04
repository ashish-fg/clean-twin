"""Inspection model for building inspections."""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    Index,
    String,
    Text,
    Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, validates

from .base import Base, TimestampMixin


class InspectionStatus(str, enum.Enum):
    """Enum for inspection status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Inspection(Base, TimestampMixin):
    """Model representing a building inspection."""

    __tablename__ = "inspections"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )

    building_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    building_address: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    inspection_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    operator_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    status: Mapped[InspectionStatus] = mapped_column(
        SQLEnum(InspectionStatus, native_enum=False, length=20),
        nullable=False,
        default=InspectionStatus.PENDING
    )

    overall_quality_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    total_area_sqm: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    video_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    report_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )

    # Table-level constraints
    __table_args__ = (
        CheckConstraint(
            "overall_quality_score IS NULL OR (overall_quality_score >= 0 AND overall_quality_score <= 100)",
            name="check_quality_score_range"
        ),
        CheckConstraint(
            "total_area_sqm > 0",
            name="check_total_area_positive"
        ),
        Index("ix_inspections_inspection_date", "inspection_date"),
        Index("ix_inspections_status", "status"),
    )

    @validates("overall_quality_score")
    def validate_quality_score(self, key: str, value: Optional[float]) -> Optional[float]:
        """Validate that quality score is within valid range (0-100) or None."""
        if value is not None:
            if value < 0 or value > 100:
                raise ValueError(
                    f"overall_quality_score must be between 0 and 100, got {value}"
                )
        return value

    @validates("total_area_sqm")
    def validate_total_area(self, key: str, value: float) -> float:
        """Validate that total area is positive."""
        if value <= 0:
            raise ValueError(
                f"total_area_sqm must be positive, got {value}"
            )
        return value

    def __repr__(self) -> str:
        """Return string representation of Inspection for debugging."""
        return (
            f"<Inspection("
            f"id={self.id}, "
            f"building_name='{self.building_name}', "
            f"inspection_date={self.inspection_date.isoformat() if self.inspection_date else None}, "
            f"operator_name='{self.operator_name}', "
            f"status={self.status.value}, "
            f"total_area_sqm={self.total_area_sqm}"
            f")>"
        )
