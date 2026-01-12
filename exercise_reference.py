from sqlalchemy import Column, String, Text, DateTime, func, UniqueConstraint, Index
from base import Base
import uuid


class ExerciseReference(Base):
    """
    Exercise reference model - master list of all recognized exercises.
    This table contains all exercises that have been scraped from strengthlevel.com
    and serves as the authoritative source for valid exercises in the system.

    Users can only create exercises that reference entries in this table.
    """
    __tablename__ = "exercise_references"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Exercise identification
    name = Column(String(200), nullable=False, unique=True, index=True)
    # e.g., "Bench Press", "Squat", "Deadlift"

    slug = Column(String(200), nullable=False, unique=True, index=True)
    # e.g., "bench-press", "squat", "deadlift" - matches the scraped data files

    # Optional description or notes about the exercise
    description = Column(Text, nullable=True)

    # Category/muscle group (can be added later based on needs)
    category = Column(String(100), nullable=True, index=True)
    # e.g., "chest", "legs", "back", "shoulders", "arms"

    # Equipment type (can be added later)
    equipment = Column(String(100), nullable=True, index=True)
    # e.g., "barbell", "dumbbell", "machine", "cable", "bodyweight"

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships (will be used by Exercise and ExerciseStandard models)
    # exercises = relationship("Exercise", back_populates="exercise_reference")
    # exercise_standards = relationship("ExerciseStandard", back_populates="exercise_reference")

    def __repr__(self):
        return f"<ExerciseReference(id={self.id}, name={self.name}, slug={self.slug})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "category": self.category,
            "equipment": self.equipment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
