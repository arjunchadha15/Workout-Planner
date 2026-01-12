"""
Exercise selection and ranking logic for plan generation.
Filters and prioritizes exercises based on user profile and constraints.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class ExerciseSelector:
    """
    Handles exercise selection, filtering, and ranking for plan generation.
    """
    
    # Equipment categories
    EQUIPMENT_REQUIREMENTS = {
        'full_gym': ['barbell', 'dumbbell', 'machine', 'cable', 'bodyweight'],
        'dumbbells_only': ['dumbbell', 'bodyweight'],
        'home_gym': ['dumbbell', 'bodyweight', 'bands'],
        'bodyweight_only': ['bodyweight'],
    }
    
    # Core compound movements (highest priority)
    CORE_COMPOUNDS = [
        'bench-press', 'squat', 'deadlift', 'overhead-press', 'shoulder-press',
        'bent-over-row', 'pull-ups', 'barbell-row'
    ]
    
    # Goal-specific exercise priorities
    GOAL_PRIORITIES = {
        'strength': {
            'preferred_rep_range': '3-6',
            'preferred_equipment': ['barbell'],
            'prioritize_compounds': True,
            'movement_focus': ['compound', 'heavy']
        },
        'hypertrophy': {
            'preferred_rep_range': '8-12',
            'preferred_equipment': ['dumbbell', 'cable', 'machine'],
            'prioritize_compounds': True,
            'movement_focus': ['compound', 'isolation']
        },
        'weight_loss': {
            'preferred_rep_range': '12-15',
            'preferred_equipment': ['dumbbell', 'bodyweight', 'cable'],
            'prioritize_compounds': True,
            'movement_focus': ['compound', 'circuit-friendly']
        },
        'general_fitness': {
            'preferred_rep_range': '8-12',
            'preferred_equipment': ['dumbbell', 'bodyweight'],
            'prioritize_compounds': True,
            'movement_focus': ['compound', 'functional']
        }
    }
    
    def __init__(self, db: Session, exercise_ref_repo, exercise_standard_repo):
        """
        Initialize the exercise selector.
        
        Args:
            db: Database session
            exercise_ref_repo: ExerciseReferenceRepository instance
            exercise_standard_repo: ExerciseStandardRepository instance
        """
        self.db = db
        self.exercise_ref_repo = exercise_ref_repo
        self.exercise_standard_repo = exercise_standard_repo
    
    def select_exercises(
        self,
        user_profile: Dict[str, Any],
        constraints: Dict[str, Any],
        max_exercises: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Select and rank exercises based on user profile and constraints.
        
        Args:
            user_profile: Dict with 'gender', 'bodyweight_lb', 'experience', 'goal'
            constraints: Dict with 'equipment_access', 'session_length_minutes'
            max_exercises: Maximum number of exercises to return
            
        Returns:
            List of exercise dicts with metadata for OpenAI
        """
        goal = user_profile.get('goal', 'general_fitness')
        equipment_access = constraints.get('equipment_access', 'full_gym')
        experience = user_profile.get('experience', 'intermediate')
        gender = user_profile.get('gender', 'male')
        bodyweight_lb = user_profile.get('bodyweight_lb', 150.0)
        
        # Get allowed equipment types
        allowed_equipment = self.EQUIPMENT_REQUIREMENTS.get(
            equipment_access,
            self.EQUIPMENT_REQUIREMENTS['full_gym']
        )
        
        # Fetch all exercises from database
        all_exercises = self.exercise_ref_repo.get_all()
        
        # Filter by equipment
        filtered_exercises = [
            ex for ex in all_exercises
            if ex.equipment in allowed_equipment or ex.equipment is None
        ]
        
        logger.info(
            f"Filtered {len(filtered_exercises)} exercises from {len(all_exercises)} "
            f"based on equipment: {equipment_access}"
        )
        
        # Rank exercises
        ranked_exercises = self._rank_exercises(
            filtered_exercises,
            goal=goal,
            experience=experience,
            gender=gender,
            bodyweight_lb=bodyweight_lb
        )
        
        # Limit to max_exercises
        selected = ranked_exercises[:max_exercises]
        
        # Convert to simplified format for OpenAI
        exercise_list = []
        for ex_ref, score in selected:
            # Get suggested weight
            standards = self.exercise_standard_repo.get_standard_interpolated(
                db=self.db,
                exercise_slug=ex_ref.slug,
                gender=gender,
                bodyweight_lb=bodyweight_lb
            )
            
            suggested_weight = None
            if standards and 'standards' in standards:
                level_key = f"{experience}_lb"
                suggested_weight = standards['standards'].get(level_key)
            
            exercise_list.append({
                'exercise_id': ex_ref.slug,
                'name': ex_ref.name,
                'category': ex_ref.category or 'general',
                'equipment': ex_ref.equipment or 'unknown',
                'suggested_weight_lb': suggested_weight,
                'rank_score': score
            })
        
        logger.info(f"Selected {len(exercise_list)} exercises for plan generation")
        return exercise_list
    
    def _rank_exercises(
        self,
        exercises: List,
        goal: str,
        experience: str,
        gender: str,
        bodyweight_lb: float
    ) -> List[tuple]:
        """
        Rank exercises based on goal and user profile.
        
        Returns:
            List of (exercise_reference, score) tuples, sorted by score descending
        """
        goal_prefs = self.GOAL_PRIORITIES.get(goal, self.GOAL_PRIORITIES['general_fitness'])
        
        scored_exercises = []
        for ex_ref in exercises:
            score = 0.0
            
            # Core compound exercises get highest priority
            if ex_ref.slug in self.CORE_COMPOUNDS:
                score += 100.0
            
            # Category matching (if available)
            if ex_ref.category:
                score += 10.0
            
            # Equipment preference matching
            if ex_ref.equipment in goal_prefs.get('preferred_equipment', []):
                score += 20.0
            
            # Check if exercise has standards data (indicates it's well-established)
            standards = self.exercise_standard_repo.get_standard_interpolated(
                db=self.db,
                exercise_slug=ex_ref.slug,
                gender=gender,
                bodyweight_lb=bodyweight_lb
            )
            if standards:
                score += 30.0
            
            scored_exercises.append((ex_ref, score))
        
        # Sort by score descending
        scored_exercises.sort(key=lambda x: x[1], reverse=True)
        
        return scored_exercises
