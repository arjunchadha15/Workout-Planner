"""
Cardio Reference Model
Represents available cardio exercise types in the database.
"""
from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CardioReference(Base):
    """
    Model for cardio exercise references.
    Similar to ExerciseReference but for cardio activities.
    """
    __tablename__ = 'cardio_references'
    
    id = Column(String, primary_key=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String)  # indoor, outdoor, water, etc.
    equipment = Column(String)  # machine, none, pool, etc.
    description = Column(Text)
    
    def __repr__(self):
        return f"<CardioReference(slug='{self.slug}', name='{self.name}')>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'category': self.category,
            'equipment': self.equipment,
            'description': self.description
        }
