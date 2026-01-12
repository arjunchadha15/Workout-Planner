from sqlalchemy.orm import Session
from sqlalchemy import or_
from exercise_reference import ExerciseReference
from typing import Optional, List


class ExerciseReferenceRepository:
    """Repository for exercise reference operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, exercise_reference_id: str) -> Optional[ExerciseReference]:
        """Get exercise reference by ID"""
        return self.db.query(ExerciseReference).filter(
            ExerciseReference.id == exercise_reference_id
        ).first()

    def get_by_slug(self, slug: str) -> Optional[ExerciseReference]:
        """Get exercise reference by slug (e.g., 'bench-press')"""
        return self.db.query(ExerciseReference).filter(
            ExerciseReference.slug == slug
        ).first()

    def get_by_name(self, name: str) -> Optional[ExerciseReference]:
        """Get exercise reference by exact name (e.g., 'Bench Press')"""
        return self.db.query(ExerciseReference).filter(
            ExerciseReference.name == name
        ).first()

    def search_by_name(self, search_term: str) -> List[ExerciseReference]:
        """Search exercise references by name (case-insensitive partial match)"""
        search_pattern = f"%{search_term}%"
        return self.db.query(ExerciseReference).filter(
            ExerciseReference.name.ilike(search_pattern)
        ).order_by(ExerciseReference.name).all()

    def get_all(
        self,
        category: Optional[str] = None,
        equipment: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ExerciseReference]:
        """
        Get all exercise references with optional filtering

        Args:
            category: Filter by category (e.g., 'chest', 'legs')
            equipment: Filter by equipment type (e.g., 'barbell', 'dumbbell')
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
        """
        query = self.db.query(ExerciseReference)

        if category:
            query = query.filter(ExerciseReference.category == category)

        if equipment:
            query = query.filter(ExerciseReference.equipment == equipment)

        query = query.order_by(ExerciseReference.name)

        if offset:
            query = query.offset(offset)

        if limit:
            query = query.limit(limit)

        return query.all()

    def count_all(
        self,
        category: Optional[str] = None,
        equipment: Optional[str] = None
    ) -> int:
        """Count all exercise references with optional filtering"""
        query = self.db.query(ExerciseReference)

        if category:
            query = query.filter(ExerciseReference.category == category)

        if equipment:
            query = query.filter(ExerciseReference.equipment == equipment)

        return query.count()

    def create(
        self,
        name: str,
        slug: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        equipment: Optional[str] = None
    ) -> ExerciseReference:
        """Create a new exercise reference"""
        exercise_ref = ExerciseReference(
            name=name,
            slug=slug,
            description=description,
            category=category,
            equipment=equipment
        )
        self.db.add(exercise_ref)
        self.db.commit()
        self.db.refresh(exercise_ref)
        return exercise_ref

    def update(
        self,
        exercise_reference_id: str,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        equipment: Optional[str] = None
    ) -> Optional[ExerciseReference]:
        """Update an existing exercise reference"""
        exercise_ref = self.get_by_id(exercise_reference_id)
        if not exercise_ref:
            return None

        if name is not None:
            exercise_ref.name = name
        if slug is not None:
            exercise_ref.slug = slug
        if description is not None:
            exercise_ref.description = description
        if category is not None:
            exercise_ref.category = category
        if equipment is not None:
            exercise_ref.equipment = equipment

        self.db.commit()
        self.db.refresh(exercise_ref)
        return exercise_ref

    def delete(self, exercise_reference_id: str) -> bool:
        """
        Delete an exercise reference

        Note: This will fail if there are exercises or standards referencing it
        due to foreign key constraints
        """
        exercise_ref = self.get_by_id(exercise_reference_id)
        if not exercise_ref:
            return False

        self.db.delete(exercise_ref)
        self.db.commit()
        return True

    def get_categories(self) -> List[str]:
        """Get list of unique categories"""
        results = self.db.query(ExerciseReference.category).filter(
            ExerciseReference.category.isnot(None)
        ).distinct().order_by(ExerciseReference.category).all()
        return [r[0] for r in results]

    def get_equipment_types(self) -> List[str]:
        """Get list of unique equipment types"""
        results = self.db.query(ExerciseReference.equipment).filter(
            ExerciseReference.equipment.isnot(None)
        ).distinct().order_by(ExerciseReference.equipment).all()
        return [r[0] for r in results]
