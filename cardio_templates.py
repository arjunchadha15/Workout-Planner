"""
Cardio templates for workout plan generation.
Provides structured cardio options that OpenAI can select from.
"""
from typing import List, Dict, Any


class CardioTemplates:
    """Repository of cardio workout templates"""
    
    # Cardio template definitions
    TEMPLATES = [
        {
            "cardio_template_id": "zone2_steady_v1",
            "name": "Zone 2 Steady State Cardio",
            "description": "Low-intensity steady-state cardio for fat burning and aerobic base",
            "default_duration_minutes": 20,
            "intensity_target": {
                "type": "rpe",
                "target": 5,
                "description": "RPE 5/10 - conversational pace"
            },
            "exercise_options": ["treadmill walk", "bike", "elliptical", "rowing"],
            "suitable_for_goals": ["weight_loss", "general_fitness"]
        },
        {
            "cardio_template_id": "hiit_intervals_v1",
            "name": "HIIT Intervals",
            "description": "High-intensity interval training for maximum calorie burn",
            "default_duration_minutes": 15,
            "intensity_target": {
                "type": "intervals",
                "work_seconds": 30,
                "rest_seconds": 30,
                "description": "30s high intensity / 30s recovery"
            },
            "exercise_options": ["bike sprints", "rowing sprints", "treadmill sprints"],
            "suitable_for_goals": ["weight_loss", "general_fitness"]
        },
        {
            "cardio_template_id": "liss_long_v1",
            "name": "LISS - Long Duration",
            "description": "Low-intensity steady state for 30+ minutes",
            "default_duration_minutes": 30,
            "intensity_target": {
                "type": "rpe",
                "target": 4,
                "description": "RPE 4/10 - very easy pace"
            },
            "exercise_options": ["treadmill walk", "bike", "elliptical"],
            "suitable_for_goals": ["weight_loss", "general_fitness"]
        },
        {
            "cardio_template_id": "active_recovery_v1",
            "name": "Active Recovery",
            "description": "Very light cardio for recovery days",
            "default_duration_minutes": 15,
            "intensity_target": {
                "type": "rpe",
                "target": 3,
                "description": "RPE 3/10 - minimal effort"
            },
            "exercise_options": ["walk", "light bike", "stretching/yoga"],
            "suitable_for_goals": ["strength", "hypertrophy", "weight_loss", "general_fitness"]
        },
        {
            "cardio_template_id": "conditioning_circuit_v1",
            "name": "Conditioning Circuit",
            "description": "Circuit-style cardio for athletic conditioning",
            "default_duration_minutes": 20,
            "intensity_target": {
                "type": "circuit",
                "rounds": 4,
                "description": "4 rounds of varied exercises"
            },
            "exercise_options": ["jump rope", "burpees", "mountain climbers", "battle ropes"],
            "suitable_for_goals": ["general_fitness", "weight_loss"]
        }
    ]
    
    @classmethod
    def get_all_templates(cls) -> List[Dict[str, Any]]:
        """Get all cardio templates"""
        return cls.TEMPLATES
    
    @classmethod
    def get_templates_for_goal(cls, goal: str) -> List[Dict[str, Any]]:
        """
        Get cardio templates suitable for a specific fitness goal.
        
        Args:
            goal: Fitness goal (strength, hypertrophy, weight_loss, general_fitness)
            
        Returns:
            List of suitable cardio templates
        """
        return [
            template for template in cls.TEMPLATES
            if goal in template.get("suitable_for_goals", [])
        ]
    
    @classmethod
    def get_template_by_id(cls, template_id: str) -> Dict[str, Any]:
        """
        Get a specific cardio template by ID.
        
        Args:
            template_id: The template ID
            
        Returns:
            Template dict or None if not found
        """
        for template in cls.TEMPLATES:
            if template["cardio_template_id"] == template_id:
                return template
        return None
    
    @classmethod
    def get_template_summary_for_openai(cls, goal: str) -> List[Dict[str, Any]]:
        """
        Get a simplified summary of cardio templates for OpenAI prompt.
        
        Args:
            goal: User's fitness goal
            
        Returns:
            List of simplified template dicts for OpenAI
        """
        templates = cls.get_templates_for_goal(goal)
        return [
            {
                "id": t["cardio_template_id"],
                "name": t["name"],
                "duration_min": t["default_duration_minutes"],
                "intensity": t["intensity_target"]["description"]
            }
            for t in templates
        ]
