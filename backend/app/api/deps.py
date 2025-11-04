"""API dependencies for dependency injection."""

from typing import Generator

from sqlalchemy.orm import Session

from ..database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields:
        Database session

    Example usage in endpoint:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
