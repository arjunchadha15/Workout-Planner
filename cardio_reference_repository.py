"""
Cardio Reference Repository
Database access layer for cardio references.
"""
from sqlalchemy.orm import Session
from cardio_reference import CardioReference
from typing import Optional, List


class CardioReferenceRepository:
    """Repository for cardio reference operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, cardio_id: str) -> Optional[CardioReference]:
        """Get cardio reference by ID"""
        return self.db.query(CardioReference).filter(
            CardioReference.id == cardio_id
        ).first()
    
    def get_by_slug(self, slug: str) -> Optional[CardioReference]:
        """Get cardio reference by slug (e.g., 'treadmill')"""
        return self.db.query(CardioReference).filter(
            CardioReference.slug == slug
        ).first()
    
    def get_all(
        self,
        category: Optional[str] = None,
        equipment: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[CardioReference]:
        """
        Get all cardio references with optional filtering
        
        Args:
            category: Filter by category (e.g., 'indoor', 'outdoor')
            equipment: Filter by equipment type (e.g., 'machine', 'none')
            limit: Maximum number of results
        """
        query = self.db.query(CardioReference)
        
        if category:
            query = query.filter(CardioReference.category == category)
        
        if equipment:
            query = query.filter(CardioReference.equipment == equipment)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_by_equipment_access(self, equipment_access: str) -> List[CardioReference]:
        """
        Get cardio options available for given equipment access level
        
        Args:
            equipment_access: 'full_gym', 'home_gym', 'bodyweight_only', etc.
        """
        # Define which cardio types are available for each equipment level
        equipment_map = {
            'full_gym': ['treadmill', 'stairmaster', 'elliptical', 'row-machine', 
                        'biking', 'jump-rope', 'walking', 'running'],
            'home_gym': ['jump-rope', 'walking', 'running', 'biking'],
            'dumbbells_only': ['jump-rope', 'walking', 'running'],
            'bodyweight_only': ['jump-rope', 'walking', 'running']
        }
        
        allowed_slugs = equipment_map.get(equipment_access, ['walking', 'running'])
        
        return self.db.query(CardioReference).filter(
            CardioReference.slug.in_(allowed_slugs)
        ).all()
