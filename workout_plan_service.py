from sqlalchemy.orm import Session
from app.repositories.split_repository import SplitRepository
from app.repositories.workout_day_repository import WorkoutDayRepository
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.exercise_reference_repository import ExerciseReferenceRepository
from app.repositories.exercise_standard_repository import ExerciseStandardRepository
from app.models.workout_day import WorkoutFocus
from app.middleware.error_handler import AppException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class WorkoutPlanService:
    """Service for loading prebuilt workout plans"""

    # PPL Template - 6 days, 34 exercises
    PPL_TEMPLATE = {
        "split_name": "Push Pull Legs",
        "split_description": "6-day Push Pull Legs program with progressive overload tracking",
        "workout_days": [
            {
                "day_of_week": 1,  # Monday
                "focus": WorkoutFocus.PUSH,
                "order": 0,
                "exercises": [
                    {"slug": "bench-press", "order": 0},
                    {"slug": "incline-bench-press", "order": 1},
                    {"slug": "shoulder-press", "order": 2},
                    {"slug": "dumbbell-lateral-raise", "order": 3},
                    {"slug": "dips", "order": 4},
                    {"slug": "cable-fly", "order": 5},
                ]
            },
            {
                "day_of_week": 2,  # Tuesday
                "focus": WorkoutFocus.PULL,
                "order": 1,
                "exercises": [
                    {"slug": "deadlift", "order": 0},
                    {"slug": "pull-ups", "order": 1},
                    {"slug": "bent-over-row", "order": 2},
                    {"slug": "face-pull", "order": 3},
                    {"slug": "hammer-curl", "order": 4},
                    {"slug": "preacher-curl", "order": 5},
                ]
            },
            {
                "day_of_week": 3,  # Wednesday
                "focus": WorkoutFocus.LEGS,
                "order": 2,
                "exercises": [
                    {"slug": "squat", "order": 0},
                    {"slug": "horizontal-leg-press", "order": 1},
                    {"slug": "seated-leg-curl", "order": 2},
                    {"slug": "machine-calf-raise", "order": 3},
                    {"slug": "lunge", "order": 4},
                ]
            },
            {
                "day_of_week": 4,  # Thursday
                "focus": WorkoutFocus.PUSH,
                "order": 3,
                "exercises": [
                    {"slug": "incline-bench-press", "order": 0},
                    {"slug": "dumbbell-bench-press", "order": 1},
                    {"slug": "arnold-press", "order": 2},
                    {"slug": "cable-fly", "order": 3},
                    {"slug": "tricep-extension", "order": 4},
                    {"slug": "shoulder-press", "order": 5},
                ]
            },
            {
                "day_of_week": 5,  # Friday
                "focus": WorkoutFocus.PULL,
                "order": 4,
                "exercises": [
                    {"slug": "pull-ups", "order": 0},
                    {"slug": "t-bar-row", "order": 1},
                    {"slug": "lat-pulldown", "order": 2},
                    {"slug": "machine-reverse-fly", "order": 3},
                    {"slug": "dumbbell-curl", "order": 4},
                    {"slug": "seated-cable-row", "order": 5},
                ]
            },
            {
                "day_of_week": 6,  # Saturday
                "focus": WorkoutFocus.LEGS,
                "order": 5,
                "exercises": [
                    {"slug": "front-squat", "order": 0},
                    {"slug": "romanian-deadlift", "order": 1},
                    {"slug": "leg-extension", "order": 2},
                    {"slug": "machine-calf-raise", "order": 3},
                    {"slug": "hip-thrust", "order": 4},
                ]
            }
        ]
    }

    # Upper/Lower Template - 4 days, 24 exercises
    UPPER_LOWER_TEMPLATE = {
        "split_name": "Upper Lower",
        "split_description": "4-day Upper/Lower split with progressive overload tracking",
        "workout_days": [
            {
                "day_of_week": 1,  # Monday
                "focus": WorkoutFocus.UPPER,
                "order": 0,
                "exercises": [
                    {"slug": "bench-press", "order": 0},
                    {"slug": "bent-over-row", "order": 1},
                    {"slug": "shoulder-press", "order": 2},
                    {"slug": "pull-ups", "order": 3},
                    {"slug": "dips", "order": 4},
                    {"slug": "dumbbell-curl", "order": 5},
                ]
            },
            {
                "day_of_week": 2,  # Tuesday
                "focus": WorkoutFocus.LOWER,
                "order": 1,
                "exercises": [
                    {"slug": "squat", "order": 0},
                    {"slug": "romanian-deadlift", "order": 1},
                    {"slug": "horizontal-leg-press", "order": 2},
                    {"slug": "seated-leg-curl", "order": 3},
                    {"slug": "machine-calf-raise", "order": 4},
                    {"slug": "lunge", "order": 5},
                ]
            },
            {
                "day_of_week": 4,  # Thursday
                "focus": WorkoutFocus.UPPER,
                "order": 2,
                "exercises": [
                    {"slug": "incline-bench-press", "order": 0},
                    {"slug": "seated-cable-row", "order": 1},
                    {"slug": "dumbbell-bench-press", "order": 2},
                    {"slug": "lat-pulldown", "order": 3},
                    {"slug": "dumbbell-lateral-raise", "order": 4},
                    {"slug": "hammer-curl", "order": 5},
                ]
            },
            {
                "day_of_week": 5,  # Friday
                "focus": WorkoutFocus.LOWER,
                "order": 3,
                "exercises": [
                    {"slug": "deadlift", "order": 0},
                    {"slug": "front-squat", "order": 1},
                    {"slug": "leg-extension", "order": 2},
                    {"slug": "hip-thrust", "order": 3},
                    {"slug": "machine-calf-raise", "order": 4},
                    {"slug": "split-squat", "order": 5},
                ]
            }
        ]
    }

    # Full Body Template - 3 days, 18 exercises
    FULL_BODY_TEMPLATE = {
        "split_name": "Full Body",
        "split_description": "3-day full body workout split covering all major muscle groups",
        "workout_days": [
            {
                "day_of_week": 1,  # Monday
                "focus": WorkoutFocus.FULL_BODY,
                "order": 0,
                "exercises": [
                    {"slug": "squat", "order": 0},
                    {"slug": "bench-press", "order": 1},
                    {"slug": "bent-over-row", "order": 2},
                    {"slug": "shoulder-press", "order": 3},
                    {"slug": "dumbbell-curl", "order": 4},
                    {"slug": "tricep-extension", "order": 5},
                ]
            },
            {
                "day_of_week": 3,  # Wednesday
                "focus": WorkoutFocus.FULL_BODY,
                "order": 1,
                "exercises": [
                    {"slug": "deadlift", "order": 0},
                    {"slug": "incline-bench-press", "order": 1},
                    {"slug": "pull-ups", "order": 2},
                    {"slug": "horizontal-leg-press", "order": 3},
                    {"slug": "dumbbell-lateral-raise", "order": 4},
                    {"slug": "dips", "order": 5},
                ]
            },
            {
                "day_of_week": 5,  # Friday
                "focus": WorkoutFocus.FULL_BODY,
                "order": 2,
                "exercises": [
                    {"slug": "front-squat", "order": 0},
                    {"slug": "dumbbell-bench-press", "order": 1},
                    {"slug": "seated-cable-row", "order": 2},
                    {"slug": "dumbbell-lunge", "order": 3},
                    {"slug": "face-pull", "order": 4},
                    {"slug": "hammer-curl", "order": 5},
                ]
            }
        ]
    }

    # Bro Split Template - 5 days, 25 exercises
    BRO_SPLIT_TEMPLATE = {
        "split_name": "Bro Split",
        "split_description": "5-day body part split focusing on one muscle group per day",
        "workout_days": [
            {
                "day_of_week": 1,  # Monday
                "focus": WorkoutFocus.CHEST,
                "order": 0,
                "exercises": [
                    {"slug": "bench-press", "order": 0},
                    {"slug": "incline-bench-press", "order": 1},
                    {"slug": "cable-fly", "order": 2},
                    {"slug": "dumbbell-bench-press", "order": 3},
                    {"slug": "dips", "order": 4},
                ]
            },
            {
                "day_of_week": 2,  # Tuesday
                "focus": WorkoutFocus.BACK,
                "order": 1,
                "exercises": [
                    {"slug": "deadlift", "order": 0},
                    {"slug": "pull-ups", "order": 1},
                    {"slug": "bent-over-row", "order": 2},
                    {"slug": "lat-pulldown", "order": 3},
                    {"slug": "seated-cable-row", "order": 4},
                ]
            },
            {
                "day_of_week": 3,  # Wednesday
                "focus": WorkoutFocus.SHOULDERS,
                "order": 2,
                "exercises": [
                    {"slug": "shoulder-press", "order": 0},
                    {"slug": "dumbbell-lateral-raise", "order": 1},
                    {"slug": "dumbbell-front-raise", "order": 2},
                    {"slug": "face-pull", "order": 3},
                    {"slug": "dumbbell-shrug", "order": 4},
                ]
            },
            {
                "day_of_week": 4,  # Thursday
                "focus": WorkoutFocus.LEGS,
                "order": 3,
                "exercises": [
                    {"slug": "squat", "order": 0},
                    {"slug": "horizontal-leg-press", "order": 1},
                    {"slug": "seated-leg-curl", "order": 2},
                    {"slug": "machine-calf-raise", "order": 3},
                    {"slug": "dumbbell-lunge", "order": 4},
                ]
            },
            {
                "day_of_week": 5,  # Friday
                "focus": WorkoutFocus.ARMS,
                "order": 4,
                "exercises": [
                    {"slug": "dumbbell-curl", "order": 0},
                    {"slug": "tricep-extension", "order": 1},
                    {"slug": "hammer-curl", "order": 2},
                    {"slug": "dips", "order": 3},
                    {"slug": "preacher-curl", "order": 4},
                ]
            }
        ]
    }

    DEFAULT_WEIGHT_LB = 45.0
    DEFAULT_SETS = 3
    DEFAULT_REPS = 8

    def __init__(self, db: Session):
        self.db = db
        self.split_repo = SplitRepository(db)
        self.workout_day_repo = WorkoutDayRepository(db)
        self.exercise_repo = ExerciseRepository(db)
        self.exercise_ref_repo = ExerciseReferenceRepository(db)
        self.exercise_standard_repo = ExerciseStandardRepository()

    def load_ppl_plan(
        self,
        user_id: str,
        level: str,
        user_bodyweight_lb: float,
        user_gender: str
    ) -> Dict[str, Any]:
        """
        Load the PPL workout plan for a user.

        Args:
            user_id: User's ID
            level: Workout difficulty level (beginner, novice, intermediate, advanced, elite)
            user_bodyweight_lb: User's bodyweight in pounds
            user_gender: User's gender (male or female)

        Returns:
            Dict with split_id, split_name, total_workout_days, total_exercises, message

        Raises:
            AppException: If exercise reference not found or database error
        """
        logger.info(f"Loading PPL plan for user {user_id} at {level} level")

        try:
            # Step 1: Deactivate existing splits
            self._deactivate_existing_splits(user_id)

            # Step 2: Create new split
            split = self.split_repo.create_split(
                user_id=user_id,
                name=self.PPL_TEMPLATE["split_name"],
                description=self.PPL_TEMPLATE["split_description"],
                is_active=True
            )

            # Step 3: Create workout days with exercises
            total_exercises_created = 0

            for day_template in self.PPL_TEMPLATE["workout_days"]:
                # Create workout day
                workout_day = self.workout_day_repo.create_workout_day(
                    split_id=split.id,
                    day_of_week=day_template["day_of_week"],
                    focus=day_template["focus"],
                    order=day_template["order"]
                )

                # Create exercises for this day
                for exercise_template in day_template["exercises"]:
                    # Lookup exercise reference
                    exercise_ref = self.exercise_ref_repo.get_by_slug(exercise_template["slug"])

                    if not exercise_ref:
                        # Rollback and raise error
                        self.db.rollback()
                        raise AppException(
                            status_code=404,
                            message=f"Exercise '{exercise_template['slug']}' not found in database"
                        )

                    # Get initial weight from standards
                    weight_lb = self._get_exercise_weight(
                        exercise_slug=exercise_template["slug"],
                        level=level,
                        bodyweight_lb=user_bodyweight_lb,
                        gender=user_gender
                    )

                    # Create exercise with notes and initial last_* values
                    notes = f"{self.DEFAULT_SETS} sets x {self.DEFAULT_REPS} reps @ {weight_lb} lbs"
                    exercise = self.exercise_repo.create_exercise(
                        workout_day_id=workout_day.id,
                        exercise_reference_id=exercise_ref.id,
                        order=exercise_template["order"],
                        notes=notes,
                        last_sets=self.DEFAULT_SETS,
                        last_reps=self.DEFAULT_REPS,
                        last_weight=int(weight_lb)
                    )

                    total_exercises_created += 1

            # Commit transaction
            self.db.commit()

            logger.info(f"Successfully created PPL plan for user {user_id}: {total_exercises_created} exercises")

            return {
                "split_id": split.id,
                "split_name": split.name,
                "total_workout_days": len(self.PPL_TEMPLATE["workout_days"]),
                "total_exercises": total_exercises_created,
                "message": "PPL workout plan created successfully"
            }

        except AppException:
            # Re-raise AppException as-is
            raise
        except Exception as e:
            # Rollback and raise generic error
            self.db.rollback()
            logger.error(f"Failed to create PPL plan for user {user_id}: {e}")
            raise AppException(
                status_code=500,
                message="Failed to create workout plan"
            )

    def load_upper_lower_plan(
        self,
        user_id: str,
        level: str,
        user_bodyweight_lb: float,
        user_gender: str
    ) -> Dict[str, Any]:
        """
        Load the Upper/Lower workout plan for a user.

        Args:
            user_id: User's ID
            level: Workout difficulty level (beginner, novice, intermediate, advanced, elite)
            user_bodyweight_lb: User's bodyweight in pounds
            user_gender: User's gender (male or female)

        Returns:
            Dict with split_id, split_name, total_workout_days, total_exercises, message

        Raises:
            AppException: If exercise reference not found or database error
        """
        logger.info(f"Loading Upper/Lower plan for user {user_id} at {level} level")

        try:
            # Step 1: Deactivate existing splits
            self._deactivate_existing_splits(user_id)

            # Step 2: Create new split
            split = self.split_repo.create_split(
                user_id=user_id,
                name=self.UPPER_LOWER_TEMPLATE["split_name"],
                description=self.UPPER_LOWER_TEMPLATE["split_description"],
                is_active=True
            )

            # Step 3: Create workout days with exercises
            total_exercises_created = 0

            for day_template in self.UPPER_LOWER_TEMPLATE["workout_days"]:
                # Create workout day
                workout_day = self.workout_day_repo.create_workout_day(
                    split_id=split.id,
                    day_of_week=day_template["day_of_week"],
                    focus=day_template["focus"],
                    order=day_template["order"]
                )

                # Create exercises for this day
                for exercise_template in day_template["exercises"]:
                    # Lookup exercise reference
                    exercise_ref = self.exercise_ref_repo.get_by_slug(exercise_template["slug"])

                    if not exercise_ref:
                        # Rollback and raise error
                        self.db.rollback()
                        raise AppException(
                            status_code=404,
                            message=f"Exercise '{exercise_template['slug']}' not found in database"
                        )

                    # Get initial weight from standards
                    weight_lb = self._get_exercise_weight(
                        exercise_slug=exercise_template["slug"],
                        level=level,
                        bodyweight_lb=user_bodyweight_lb,
                        gender=user_gender
                    )

                    # Create exercise with notes and initial last_* values
                    notes = f"{self.DEFAULT_SETS} sets x {self.DEFAULT_REPS} reps @ {weight_lb} lbs"
                    exercise = self.exercise_repo.create_exercise(
                        workout_day_id=workout_day.id,
                        exercise_reference_id=exercise_ref.id,
                        order=exercise_template["order"],
                        notes=notes,
                        last_sets=self.DEFAULT_SETS,
                        last_reps=self.DEFAULT_REPS,
                        last_weight=int(weight_lb)
                    )

                    total_exercises_created += 1

            # Commit transaction
            self.db.commit()

            logger.info(f"Successfully created Upper/Lower plan for user {user_id}: {total_exercises_created} exercises")

            return {
                "split_id": split.id,
                "split_name": split.name,
                "total_workout_days": len(self.UPPER_LOWER_TEMPLATE["workout_days"]),
                "total_exercises": total_exercises_created,
                "message": "Upper/Lower workout plan created successfully"
            }

        except AppException:
            # Re-raise AppException as-is
            raise
        except Exception as e:
            # Rollback and raise generic error
            self.db.rollback()
            logger.error(f"Failed to create Upper/Lower plan for user {user_id}: {e}")
            raise AppException(
                status_code=500,
                message="Failed to create workout plan"
            )

    def load_full_body_plan(
        self,
        user_id: str,
        level: str,
        user_bodyweight_lb: float,
        user_gender: str
    ) -> Dict[str, Any]:
        """
        Load the Full Body workout plan for a user.

        Args:
            user_id: User's ID
            level: Workout difficulty level (beginner, novice, intermediate, advanced, elite)
            user_bodyweight_lb: User's bodyweight in pounds
            user_gender: User's gender (male or female)

        Returns:
            Dict with split_id, split_name, total_workout_days, total_exercises, message

        Raises:
            AppException: If exercise reference not found or database error
        """
        logger.info(f"Loading Full Body plan for user {user_id} at {level} level")

        try:
            # Step 1: Deactivate existing splits
            self._deactivate_existing_splits(user_id)

            # Step 2: Create new split
            split = self.split_repo.create_split(
                user_id=user_id,
                name=self.FULL_BODY_TEMPLATE["split_name"],
                description=self.FULL_BODY_TEMPLATE["split_description"],
                is_active=True
            )

            # Step 3: Create workout days with exercises
            total_exercises_created = 0

            for day_template in self.FULL_BODY_TEMPLATE["workout_days"]:
                # Create workout day
                workout_day = self.workout_day_repo.create_workout_day(
                    split_id=split.id,
                    day_of_week=day_template["day_of_week"],
                    focus=day_template["focus"],
                    order=day_template["order"]
                )

                # Create exercises for this day
                for exercise_template in day_template["exercises"]:
                    # Lookup exercise reference
                    exercise_ref = self.exercise_ref_repo.get_by_slug(exercise_template["slug"])

                    if not exercise_ref:
                        # Rollback and raise error
                        self.db.rollback()
                        raise AppException(
                            status_code=404,
                            message=f"Exercise '{exercise_template['slug']}' not found in database"
                        )

                    # Get initial weight from standards
                    weight_lb = self._get_exercise_weight(
                        exercise_slug=exercise_template["slug"],
                        level=level,
                        bodyweight_lb=user_bodyweight_lb,
                        gender=user_gender
                    )

                    # Create exercise with notes and initial last_* values
                    notes = f"{self.DEFAULT_SETS} sets x {self.DEFAULT_REPS} reps @ {weight_lb} lbs"
                    exercise = self.exercise_repo.create_exercise(
                        workout_day_id=workout_day.id,
                        exercise_reference_id=exercise_ref.id,
                        order=exercise_template["order"],
                        notes=notes,
                        last_sets=self.DEFAULT_SETS,
                        last_reps=self.DEFAULT_REPS,
                        last_weight=int(weight_lb)
                    )

                    total_exercises_created += 1

            # Commit transaction
            self.db.commit()

            logger.info(f"Successfully created Full Body plan for user {user_id}: {total_exercises_created} exercises")

            return {
                "split_id": split.id,
                "split_name": split.name,
                "total_workout_days": len(self.FULL_BODY_TEMPLATE["workout_days"]),
                "total_exercises": total_exercises_created,
                "message": "Full Body workout plan created successfully"
            }

        except AppException:
            # Re-raise AppException as-is
            raise
        except Exception as e:
            # Rollback and raise generic error
            self.db.rollback()
            logger.error(f"Failed to create Full Body plan for user {user_id}: {e}")
            raise AppException(
                status_code=500,
                message="Failed to create workout plan"
            )

    def load_bro_split_plan(
        self,
        user_id: str,
        level: str,
        user_bodyweight_lb: float,
        user_gender: str
    ) -> Dict[str, Any]:
        """
        Load the Bro Split workout plan for a user.

        Args:
            user_id: User's ID
            level: Workout difficulty level (beginner, novice, intermediate, advanced, elite)
            user_bodyweight_lb: User's bodyweight in pounds
            user_gender: User's gender (male or female)

        Returns:
            Dict with split_id, split_name, total_workout_days, total_exercises, message

        Raises:
            AppException: If exercise reference not found or database error
        """
        logger.info(f"Loading Bro Split plan for user {user_id} at {level} level")

        try:
            # Step 1: Deactivate existing splits
            self._deactivate_existing_splits(user_id)

            # Step 2: Create new split
            split = self.split_repo.create_split(
                user_id=user_id,
                name=self.BRO_SPLIT_TEMPLATE["split_name"],
                description=self.BRO_SPLIT_TEMPLATE["split_description"],
                is_active=True
            )

            # Step 3: Create workout days with exercises
            total_exercises_created = 0

            for day_template in self.BRO_SPLIT_TEMPLATE["workout_days"]:
                # Create workout day
                workout_day = self.workout_day_repo.create_workout_day(
                    split_id=split.id,
                    day_of_week=day_template["day_of_week"],
                    focus=day_template["focus"],
                    order=day_template["order"]
                )

                # Create exercises for this day
                for exercise_template in day_template["exercises"]:
                    # Lookup exercise reference
                    exercise_ref = self.exercise_ref_repo.get_by_slug(exercise_template["slug"])

                    if not exercise_ref:
                        # Rollback and raise error
                        self.db.rollback()
                        raise AppException(
                            status_code=404,
                            message=f"Exercise '{exercise_template['slug']}' not found in database"
                        )

                    # Get initial weight from standards
                    weight_lb = self._get_exercise_weight(
                        exercise_slug=exercise_template["slug"],
                        level=level,
                        bodyweight_lb=user_bodyweight_lb,
                        gender=user_gender
                    )

                    # Create exercise with notes and initial last_* values
                    notes = f"{self.DEFAULT_SETS} sets x {self.DEFAULT_REPS} reps @ {weight_lb} lbs"
                    exercise = self.exercise_repo.create_exercise(
                        workout_day_id=workout_day.id,
                        exercise_reference_id=exercise_ref.id,
                        order=exercise_template["order"],
                        notes=notes,
                        last_sets=self.DEFAULT_SETS,
                        last_reps=self.DEFAULT_REPS,
                        last_weight=int(weight_lb)
                    )

                    total_exercises_created += 1

            # Commit transaction
            self.db.commit()

            logger.info(f"Successfully created Bro Split plan for user {user_id}: {total_exercises_created} exercises")

            return {
                "split_id": split.id,
                "split_name": split.name,
                "total_workout_days": len(self.BRO_SPLIT_TEMPLATE["workout_days"]),
                "total_exercises": total_exercises_created,
                "message": "Bro Split workout plan created successfully"
            }

        except AppException:
            # Re-raise AppException as-is
            raise
        except Exception as e:
            # Rollback and raise generic error
            self.db.rollback()
            logger.error(f"Failed to create Bro Split plan for user {user_id}: {e}")
            raise AppException(
                status_code=500,
                message="Failed to create workout plan"
            )

    def _deactivate_existing_splits(self, user_id: str) -> None:
        """Deactivate all user's active splits"""
        self.split_repo.deactivate_all_splits(user_id)
        logger.info(f"Deactivated existing splits for user {user_id}")

    def _get_exercise_weight(
        self,
        exercise_slug: str,
        level: str,
        bodyweight_lb: float,
        gender: str
    ) -> float:
        """
        Get initial weight for an exercise based on standards.
        Falls back to default if no standards found.

        Args:
            exercise_slug: Exercise slug (e.g., 'bench-press')
            level: Difficulty level (beginner, novice, etc.)
            bodyweight_lb: User's bodyweight in pounds
            gender: User's gender (male or female)

        Returns:
            Weight in pounds
        """
        # Lookup standards
        standards = self.exercise_standard_repo.get_standard_interpolated(
            db=self.db,
            exercise_slug=exercise_slug,
            gender=gender,
            bodyweight_lb=bodyweight_lb
        )

        if not standards or "standards" not in standards:
            # No standards available - use default
            logger.warning(f"No standards found for {exercise_slug}, using default weight {self.DEFAULT_WEIGHT_LB} lbs")
            return self.DEFAULT_WEIGHT_LB

        # Extract weight for the specified level
        level_weights = standards["standards"]
        weight_key = f"{level}_lb"
        weight = level_weights.get(weight_key)

        if weight is None:
            logger.warning(f"No {level} weight found for {exercise_slug}, using default weight {self.DEFAULT_WEIGHT_LB} lbs")
            return self.DEFAULT_WEIGHT_LB

        return float(weight)
