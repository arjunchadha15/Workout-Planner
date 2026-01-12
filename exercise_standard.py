from sqlalchemy import Column, String, Integer, Float, UniqueConstraint, Index, ForeignKey
from base import Base
import uuid


class ExerciseStandard(Base):
    """
    Exercise standards model for strength standards data.
    Stores strength standards for different exercises based on bodyweight and gender.

    Table structure optimized for:
    - Quick lookups by exercise reference and gender
    - Efficient queries for user's bodyweight range
    - Support for interpolation between bodyweight values
    """
    __tablename__ = "exercise_standards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Exercise identification - now uses foreign key to exercise_references
    exercise_reference_id = Column(String, ForeignKey("exercise_references.id", ondelete="CASCADE"), nullable=False, index=True)

    gender = Column(String(10), nullable=False, index=True)
    # "male" or "female"
    
    # Bodyweight in pounds
    bodyweight_lb = Column(Integer, nullable=False, index=True)
    
    # Strength standards in pounds for each level
    beginner_lb = Column(Integer, nullable=False)
    novice_lb = Column(Integer, nullable=False)
    intermediate_lb = Column(Integer, nullable=False)
    advanced_lb = Column(Integer, nullable=False)
    elite_lb = Column(Integer, nullable=False)
    
    # Relationships
    # exercise_reference = relationship("ExerciseReference", back_populates="exercise_standards")

    # Composite unique constraint to prevent duplicates
    __table_args__ = (
        UniqueConstraint('exercise_reference_id', 'gender', 'bodyweight_lb',
                        name='uix_exercise_gender_bodyweight'),
        # Composite index for common query pattern
        Index('ix_exercise_standards_lookup', 'exercise_reference_id', 'gender', 'bodyweight_lb'),
    )
    
    def __repr__(self):
        return (f"<ExerciseStandard(exercise_ref_id={self.exercise_reference_id}, "
                f"gender={self.gender}, bw={self.bodyweight_lb}lb, "
                f"elite={self.elite_lb}lb)>")
    
    def get_level_for_weight(self, weight_lifted: float) -> str:
        """
        Determine the strength level for a given lifted weight.
        
        Args:
            weight_lifted: Weight lifted in pounds
            
        Returns:
            Strength level: "untrained", "beginner", "novice", "intermediate", "advanced", or "elite"
        """
        if weight_lifted < self.beginner_lb:
            return "untrained"
        elif weight_lifted < self.novice_lb:
            return "beginner"
        elif weight_lifted < self.intermediate_lb:
            return "novice"
        elif weight_lifted < self.advanced_lb:
            return "intermediate"
        elif weight_lifted < self.elite_lb:
            return "advanced"
        else:
            return "elite"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "exercise_reference_id": self.exercise_reference_id,
            "gender": self.gender,
            "bodyweight_lb": self.bodyweight_lb,
            "standards": {
                "beginner": self.beginner_lb,
                "novice": self.novice_lb,
                "intermediate": self.intermediate_lb,
                "advanced": self.advanced_lb,
                "elite": self.elite_lb
            }
        }
