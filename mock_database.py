"""
Mock database setup for testing without full app integration.
This creates stub functions so the API can run for testing.
"""

def get_db():
    """Mock database session generator"""
    # For now, return None - you'll integrate with your real DB later
    yield None

# Mock repository classes for testing
class MockExerciseReferenceRepository:
    def __init__(self, db):
        self.db = db
    
    def get_all(self):
        """Return mock exercises for testing"""
        return [
            type('Exercise', (), {
                'id': 'bench-press',
                'slug': 'bench-press',
                'name': 'Bench Press',
                'category': 'chest',
                'equipment': 'barbell'
            })(),
            type('Exercise', (), {
                'id': 'squat',
                'slug': 'squat',
                'name': 'Squat',
                'category': 'legs',
                'equipment': 'barbell'
            })(),
            # Add more exercises as needed
        ]

class MockExerciseStandardRepository:
    def get_standard_interpolated(self, db, exercise_slug, gender, bodyweight_lb):
        """Return mock standards"""
        return {
            'standards': {
                'beginner_lb': 95,
                'intermediate_lb': 135,
                'advanced_lb': 185
            }
        }
