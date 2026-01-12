"""
Cardio Selector Service
Handles cardio selection and filtering based on user profile and constraints.
"""
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CardioSelector:
    """
    Service for selecting appropriate cardio exercises.
    Similar to ExerciseSelector but for cardio activities.
    """
    
    # Default zones and durations by goal
    GOAL_DEFAULTS = {
        'strength': {
            'zone': 'zone2',
            'duration_min': 15,
            'frequency': 'optional'
        },
        'hypertrophy': {
            'zone': 'zone2',
            'duration_min': 15,
            'frequency': 'optional'
        },
        'weight_loss': {
            'zone': 'zone3',  # Moderate-high intensity, no HIIT
            'duration_min': 30,
            'frequency': 'required'
        },
        'general_fitness': {
            'zone': 'zone2',
            'duration_min': 20,
            'frequency': 'recommended'
        }
    }
    
    # Equipment requirements for cardio types
    EQUIPMENT_REQUIREMENTS = {
        'full_gym': ['machine', 'none'],
        'home_gym': ['none', 'minimal'],
        'dumbbells_only': ['none'],
        'bodyweight_only': ['none']
    }
    
    def __init__(self, db, cardio_ref_repo):
        """
        Initialize the cardio selector.
        
        Args:
            db: Database session
            cardio_ref_repo: CardioReferenceRepository instance
        """
        self.db = db
        self.cardio_ref_repo = cardio_ref_repo
    
    def select_cardio_options(
        self,
        user_profile: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Select available cardio options based on user profile and constraints.
        
        Args:
            user_profile: Dict with 'goal'
            constraints: Dict with 'equipment_access'
            
        Returns:
            List of cardio option dicts with metadata for OpenAI
        """
        goal = user_profile.get('goal', 'general_fitness')
        equipment_access = constraints.get('equipment_access', 'full_gym')
        
        # Get goal defaults
        defaults = self.GOAL_DEFAULTS.get(goal, self.GOAL_DEFAULTS['general_fitness'])
        
        # Fetch cardio options from database
        all_cardio = self.cardio_ref_repo.get_by_equipment_access(equipment_access)
        
        logger.info(
            f"Selected {len(all_cardio)} cardio options for "
            f"goal={goal}, equipment={equipment_access}"
        )
        
        # Convert to simplified format for OpenAI
        cardio_list = []
        for cardio_ref in all_cardio:
            cardio_list.append({
                'cardio_id': cardio_ref.slug,
                'name': cardio_ref.name,
                'category': cardio_ref.category,
                'equipment': cardio_ref.equipment,
                'default_zone': defaults['zone'],
                'default_duration_min': defaults['duration_min']
            })
        
        logger.info(f"Prepared {len(cardio_list)} cardio options for plan generation")
        return cardio_list
    
    def get_zone_for_goal(self, goal: str) -> str:
        """Get recommended zone for a goal"""
        return self.GOAL_DEFAULTS.get(goal, {}).get('zone', 'zone2')
    
    def get_duration_for_goal(self, goal: str) -> int:
        """Get recommended duration for a goal"""
        return self.GOAL_DEFAULTS.get(goal, {}).get('duration_min', 20)
