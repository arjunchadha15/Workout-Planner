from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import Optional
from exercise_standard import ExerciseStandard
from exercise_reference import ExerciseReference


class ExerciseStandardRepository:
    """Repository for exercise standards data access"""

    def get_standard(
        self,
        db: Session,
        exercise_slug: str,
        gender: str,
        bodyweight_lb: int
    ) -> Optional[ExerciseStandard]:
        """
        Get exact exercise standard for specific bodyweight.

        Args:
            db: Database session
            exercise_slug: Exercise slug (e.g., "bench-press")
            gender: "male" or "female"
            bodyweight_lb: Bodyweight in pounds

        Returns:
            ExerciseStandard or None if not found
        """
        return db.query(ExerciseStandard).join(
            ExerciseReference, ExerciseStandard.exercise_reference_id == ExerciseReference.id
        ).filter(
            ExerciseReference.slug == exercise_slug,
            ExerciseStandard.gender == gender,
            ExerciseStandard.bodyweight_lb == bodyweight_lb
        ).first()
    
    def get_standard_interpolated(
        self,
        db: Session,
        exercise_slug: str,
        gender: str,
        bodyweight_lb: float
    ) -> Optional[dict]:
        """
        Get interpolated exercise standards for any bodyweight.
        Uses linear interpolation between the two closest bodyweight values.

        Args:
            db: Database session
            exercise_slug: Exercise slug (e.g., "bench-press")
            gender: "male" or "female"
            bodyweight_lb: Bodyweight in pounds (can be decimal)

        Returns:
            Dictionary with interpolated standards or None if exercise not found
        """
        # Round to nearest integer for lookup
        bodyweight_int = int(round(bodyweight_lb))

        # Try exact match first
        exact = self.get_standard(db, exercise_slug, gender, bodyweight_int)
        if exact:
            result = exact.to_dict()
            # Add exercise name from reference
            exercise_ref = db.query(ExerciseReference).filter(
                ExerciseReference.id == exact.exercise_reference_id
            ).first()
            if exercise_ref:
                result["exercise_name"] = exercise_ref.name
                result["exercise_slug"] = exercise_ref.slug
            return result

        # Get the two closest bodyweights
        lower = db.query(ExerciseStandard).join(
            ExerciseReference, ExerciseStandard.exercise_reference_id == ExerciseReference.id
        ).filter(
            ExerciseReference.slug == exercise_slug,
            ExerciseStandard.gender == gender,
            ExerciseStandard.bodyweight_lb <= bodyweight_lb
        ).order_by(ExerciseStandard.bodyweight_lb.desc()).first()

        upper = db.query(ExerciseStandard).join(
            ExerciseReference, ExerciseStandard.exercise_reference_id == ExerciseReference.id
        ).filter(
            ExerciseReference.slug == exercise_slug,
            ExerciseStandard.gender == gender,
            ExerciseStandard.bodyweight_lb >= bodyweight_lb
        ).order_by(ExerciseStandard.bodyweight_lb.asc()).first()

        # Get exercise reference for metadata
        exercise_ref = db.query(ExerciseReference).filter(
            ExerciseReference.slug == exercise_slug
        ).first()

        # If we have both bounds, interpolate
        if lower and upper and lower.bodyweight_lb != upper.bodyweight_lb:
            # Linear interpolation
            ratio = (bodyweight_lb - lower.bodyweight_lb) / (upper.bodyweight_lb - lower.bodyweight_lb)

            return {
                "exercise_reference_id": lower.exercise_reference_id,
                "exercise_name": exercise_ref.name if exercise_ref else exercise_slug,
                "exercise_slug": exercise_slug,
                "gender": gender,
                "bodyweight_lb": bodyweight_lb,
                "standards": {
                    "beginner": int(lower.beginner_lb + ratio * (upper.beginner_lb - lower.beginner_lb)),
                    "novice": int(lower.novice_lb + ratio * (upper.novice_lb - lower.novice_lb)),
                    "intermediate": int(lower.intermediate_lb + ratio * (upper.intermediate_lb - lower.intermediate_lb)),
                    "advanced": int(lower.advanced_lb + ratio * (upper.advanced_lb - lower.advanced_lb)),
                    "elite": int(lower.elite_lb + ratio * (upper.elite_lb - lower.elite_lb))
                }
            }
        elif lower:
            result = lower.to_dict()
            if exercise_ref:
                result["exercise_name"] = exercise_ref.name
                result["exercise_slug"] = exercise_ref.slug
            return result
        elif upper:
            result = upper.to_dict()
            if exercise_ref:
                result["exercise_name"] = exercise_ref.name
                result["exercise_slug"] = exercise_ref.slug
            return result

        return None
    
    def get_all_exercises(self, db: Session) -> list[dict]:
        """
        Get list of all unique exercises that have standards.

        Returns:
            List of dicts with exercise reference info (id, name, slug)
        """
        exercises = db.query(ExerciseReference).join(
            ExerciseStandard, ExerciseReference.id == ExerciseStandard.exercise_reference_id
        ).distinct().order_by(ExerciseReference.name).all()

        return [
            {
                "id": ex.id,
                "name": ex.name,
                "slug": ex.slug,
                "category": ex.category,
                "equipment": ex.equipment
            }
            for ex in exercises
        ]

    def get_exercises_by_gender(self, db: Session, gender: str) -> list[dict]:
        """
        Get list of exercises available for a specific gender.

        Args:
            gender: "male" or "female"

        Returns:
            List of dicts with exercise reference info (id, name, slug)
        """
        exercises = db.query(ExerciseReference).join(
            ExerciseStandard, ExerciseReference.id == ExerciseStandard.exercise_reference_id
        ).filter(
            ExerciseStandard.gender == gender
        ).distinct().order_by(ExerciseReference.name).all()

        return [
            {
                "id": ex.id,
                "name": ex.name,
                "slug": ex.slug,
                "category": ex.category,
                "equipment": ex.equipment
            }
            for ex in exercises
        ]
    
    def check_strength_level(
        self,
        db: Session,
        exercise_slug: str,
        gender: str,
        bodyweight_lb: float,
        weight_lifted_lb: float
    ) -> Optional[dict]:
        """
        Determine what strength level a user's lift represents.

        Args:
            db: Database session
            exercise_slug: Exercise slug (e.g., "bench-press")
            gender: "male" or "female"
            bodyweight_lb: User's bodyweight
            weight_lifted_lb: Weight they lifted

        Returns:
            Dictionary with level info or None if exercise not found
        """
        # Get standards (with interpolation)
        standards = self.get_standard_interpolated(db, exercise_slug, gender, bodyweight_lb)
        if not standards:
            return None

        levels = standards["standards"]

        # Determine current level
        if weight_lifted_lb < levels["beginner"]:
            current_level = "untrained"
            next_level = "beginner"
            weight_to_next = levels["beginner"] - weight_lifted_lb
        elif weight_lifted_lb < levels["novice"]:
            current_level = "beginner"
            next_level = "novice"
            weight_to_next = levels["novice"] - weight_lifted_lb
        elif weight_lifted_lb < levels["intermediate"]:
            current_level = "novice"
            next_level = "intermediate"
            weight_to_next = levels["intermediate"] - weight_lifted_lb
        elif weight_lifted_lb < levels["advanced"]:
            current_level = "intermediate"
            next_level = "advanced"
            weight_to_next = levels["advanced"] - weight_lifted_lb
        elif weight_lifted_lb < levels["elite"]:
            current_level = "advanced"
            next_level = "elite"
            weight_to_next = levels["elite"] - weight_lifted_lb
        else:
            current_level = "elite"
            next_level = None
            weight_to_next = None

        # Calculate approximate percentile
        # Elite = 100%, Untrained = 0%, interpolate between levels
        level_percentiles = {
            "untrained": 10,
            "beginner": 30,
            "novice": 50,
            "intermediate": 70,
            "advanced": 85,
            "elite": 95
        }

        return {
            "exercise_name": standards.get("exercise_name", exercise_slug),
            "exercise_slug": exercise_slug,
            "gender": gender,
            "bodyweight_lb": bodyweight_lb,
            "weight_lifted_lb": weight_lifted_lb,
            "strength_level": current_level,
            "next_level": next_level,
            "weight_to_next_level": weight_to_next,
            "percentile": level_percentiles[current_level],
            "standards": levels
        }
    
    def get_bodyweight_range(
        self,
        db: Session,
        exercise_slug: str,
        gender: str
    ) -> Optional[dict]:
        """
        Get the available bodyweight range for an exercise.

        Returns:
            Dict with min, max, and all available bodyweights
        """
        bodyweights = db.query(ExerciseStandard.bodyweight_lb).join(
            ExerciseReference, ExerciseStandard.exercise_reference_id == ExerciseReference.id
        ).filter(
            ExerciseReference.slug == exercise_slug,
            ExerciseStandard.gender == gender
        ).order_by(ExerciseStandard.bodyweight_lb).all()

        if not bodyweights:
            return None

        bw_list = [bw[0] for bw in bodyweights]

        return {
            "min": min(bw_list),
            "max": max(bw_list),
            "available": bw_list,
            "count": len(bw_list)
        }
    
    def get_statistics(self, db: Session) -> dict:
        """
        Get statistics about the exercise standards database.

        Returns:
            Dictionary with counts and statistics
        """
        total_records = db.query(ExerciseStandard).count()
        unique_exercises = db.query(distinct(ExerciseStandard.exercise_reference_id)).count()
        male_count = db.query(ExerciseStandard).filter(
            ExerciseStandard.gender == 'male'
        ).count()
        female_count = db.query(ExerciseStandard).filter(
            ExerciseStandard.gender == 'female'
        ).count()

        return {
            "total_records": total_records,
            "unique_exercises": unique_exercises,
            "male_standards": male_count,
            "female_standards": female_count
        }


# Singleton instance
exercise_standard_repo = ExerciseStandardRepository()
