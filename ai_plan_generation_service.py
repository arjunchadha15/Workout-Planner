"""
AI-powered plan generation service.
Orchestrates exercise selection, OpenAI calls, and plan storage.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import logging

from exercise_selector import ExerciseSelector
from openai_service import OpenAIService
from cardio_selector import CardioSelector
from cardio_reference_repository import CardioReferenceRepository
from mock_cardio_database import get_mock_cardio_db
from exercise_reference_repository import ExerciseReferenceRepository
from exercise_standard_repository import ExerciseStandardRepository
from constraint_parser import ConstraintParser

logger = logging.getLogger(__name__)


class AIPlanGenerationService:
    """
    Service for generating AI-powered workout plans.
    This is the main orchestrator that brings together all components.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the AI plan generation service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.exercise_ref_repo = ExerciseReferenceRepository(db)
        self.exercise_standard_repo = ExerciseStandardRepository()
        self.exercise_selector = ExerciseSelector(
            db,
            self.exercise_ref_repo,
            self.exercise_standard_repo
        )
        self.openai_service = OpenAIService()
        self.constraint_parser = ConstraintParser()
        
        # Cardio system - using mock database since cardio not in DB yet
        mock_cardio_repo = get_mock_cardio_db()
        self.cardio_selector = CardioSelector(db=None, cardio_ref_repo=mock_cardio_repo)
    
    def generate_plan(
        self,
        user_id: str,
        user_profile: Dict[str, Any],
        constraint_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete workout plan using OpenAI.
        
        Args:
            user_id: User's ID
            user_profile: Dict with:
                - goal: strength|hypertrophy|weight_loss|general_fitness
                - days_per_week: int (3-6)
                - experience: beginner|intermediate|advanced
                - gender: male|female
                - body_weight_lb: float
                - age: int
                - equipment_access: str (default "full_gym")
            constraint_text: Optional natural language constraints from user
                
        Returns:
            Dict with generated plan following the schema
            
        Raises:
            ValueError: If required fields missing
            Exception: If plan generation fails
        """
        # Validate required fields
        required_fields = ['goal', 'days_per_week', 'experience', 'gender', 'body_weight_lb', 'age']
        for field in required_fields:
            if field not in user_profile:
                raise ValueError(f"Missing required field: {field}")
        
        # Parse constraints if provided
        parsed_constraints = {}
        constraint_prompt = ""
        if constraint_text:
            parsed_constraints = self.constraint_parser.parse_constraints(
                constraint_text,
                user_profile
            )
            constraint_prompt = self.constraint_parser.format_constraints_for_openai(
                parsed_constraints
            )
            
            # Apply equipment constraint if specified
            if parsed_constraints.get('equipment_access'):
                user_profile['equipment_access'] = parsed_constraints['equipment_access']
        
        # Set defaults
        user_profile.setdefault('equipment_access', 'full_gym')
        
        logger.info(
            f"Starting AI plan generation for user {user_id}: "
            f"goal={user_profile['goal']}, days={user_profile['days_per_week']}"
        )
        
        # Step 1: Select prioritized exercises
        logger.info("Step 1: Selecting exercises...")
        allowed_exercises = self.exercise_selector.select_exercises(
            user_profile=user_profile,
            constraints={},  # Constraints handled by parser
            max_exercises=50  # Limit for token efficiency
        )
        
        if not allowed_exercises:
            raise Exception("No exercises available for the given constraints")
        
        logger.info(f"Selected {len(allowed_exercises)} exercises")
        
        # Step 2: Get cardio options for goal
        logger.info("Step 2: Fetching cardio options...")
        allowed_cardio = self.cardio_selector.select_cardio_options(
            user_profile=user_profile,
            constraints={}  # Constraints handled by parser
        )
        logger.info(f"Available cardio options: {len(allowed_cardio)}")
        
        # Step 3: Call OpenAI to generate plan with constraints
        logger.info("Step 3: Calling OpenAI to generate plan...")
        plan_data = self.openai_service.generate_plan(
            user_profile=user_profile,
            constraints={},
            allowed_exercises=allowed_exercises,
            allowed_cardio=allowed_cardio,
            constraint_prompt=constraint_prompt  # Pass parsed constraints to OpenAI
        )
        
        logger.info("Step 4: Plan generated successfully")
        
        # Step 5: Enrich plan with full exercise metadata
        enriched_plan = self._enrich_plan_with_metadata(plan_data, allowed_exercises)
        
        # Step 6: Store plan in database (this would integrate with existing WorkoutPlanService)
        # For now, we return the plan data and let the endpoint handle storage
        
        logger.info(f"✅ AI plan generation complete for user {user_id}")
        
        return {
            "user_id": user_id,
            "plan": enriched_plan,
            "metadata": {
                "exercises_considered": len(allowed_exercises),
                "generation_method": "openai",
                "model": self.openai_service.model
            }
        }
    
    def _enrich_plan_with_metadata(
        self,
        plan_data: Dict[str, Any],
        allowed_exercises: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enrich the plan with full exercise metadata.
        
        Args:
            plan_data: Plan dict from OpenAI
            allowed_exercises: List of exercise dicts with metadata
            
        Returns:
            Enriched plan dict
        """
        # Create exercise lookup
        exercise_map = {ex['exercise_id']: ex for ex in allowed_exercises}
        
        # Enrich each exercise in the plan
        for session in plan_data.get('sessions', []):
            for block in session.get('blocks', []):
                if block.get('type') == 'strength':
                    for item in block.get('items', []):
                        exercise_id = item.get('exercise_id')
                        if exercise_id in exercise_map:
                            ex_meta = exercise_map[exercise_id]
                            # Add metadata (optional - can be used by frontend)
                            item['exercise_name'] = ex_meta['name']
                            item['category'] = ex_meta.get('category')
                            item['equipment'] = ex_meta.get('equipment')
        
        return plan_data
