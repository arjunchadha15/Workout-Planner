"""
Mock Cardio Database
Provides in-memory cardio data for testing without a real database.
"""
import uuid


class MockCardioReference:
    """Mock cardio reference object"""
    def __init__(self, slug, name, category, equipment, description=""):
        self.id = str(uuid.uuid4())
        self.slug = slug
        self.name = name
        self.category = category
        self.equipment = equipment
        self.description = description
    
    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'category': self.category,
            'equipment': self.equipment,
            'description': self.description
        }


class MockCardioReferenceRepository:
    """Mock repository with predefined cardio data"""
    
    def __init__(self):
        # Initialize mock cardio data
        self.cardio_data = [
            MockCardioReference('walking', 'Walking', 'outdoor', 'none', 'Outdoor or indoor walking'),
            MockCardioReference('treadmill', 'Treadmill', 'indoor', 'machine', 'Treadmill running or walking'),
            MockCardioReference('running', 'Running', 'outdoor', 'none', 'Outdoor running'),
            MockCardioReference('biking', 'Biking', 'indoor/outdoor', 'machine', 'Stationary or outdoor bike'),
            MockCardioReference('swimming', 'Swimming', 'water', 'pool', 'Pool swimming'),
            MockCardioReference('stairmaster', 'Stairmaster', 'indoor', 'machine', 'Stair climbing machine'),
            MockCardioReference('elliptical', 'Elliptical', 'indoor', 'machine', 'Elliptical trainer'),
            MockCardioReference('row-machine', 'Rowing Machine', 'indoor', 'machine', 'Indoor rowing ergometer'),
            MockCardioReference('jump-rope', 'Jump Rope', 'indoor/outdoor', 'minimal', 'Jump rope cardio'),
            MockCardioReference('other', 'Other', 'various', 'various', 'Other cardio activities'),
        ]
    
    def get_by_slug(self, slug: str):
        """Get cardio by slug"""
        for cardio in self.cardio_data:
            if cardio.slug == slug:
                return cardio
        return None
    
    def get_all(self, category=None, equipment=None, limit=None):
        """Get all cardio with optional filtering"""
        results = self.cardio_data
        
        if category:
            results = [c for c in results if category in c.category]
        
        if equipment:
            results = [c for c in results if c.equipment == equipment]
        
        if limit:
            results = results[:limit]
        
        return results
    
    def get_by_equipment_access(self, equipment_access: str):
        """Get cardio available for equipment level"""
        equipment_map = {
            'full_gym': ['treadmill', 'stairmaster', 'elliptical', 'row-machine', 
                        'biking', 'jump-rope', 'walking', 'running'],
            'home_gym': ['jump-rope', 'walking', 'running', 'biking'],
            'dumbbells_only': ['jump-rope', 'walking', 'running'],
            'bodyweight_only': ['jump-rope', 'walking', 'running']
        }
        
        allowed_slugs = equipment_map.get(equipment_access, ['walking', 'running'])
        
        return [c for c in self.cardio_data if c.slug in allowed_slugs]


def get_mock_cardio_db():
    """Get a mock cardio database for testing"""
    return MockCardioReferenceRepository()
