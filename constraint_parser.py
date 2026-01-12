"""
Constraint Parser - Parse natural language user constraints with guardrails.

This allows users to input custom constraints like:
- "I only have dumbbells and a pull-up bar"
- "I want to do PPL + Arnold split"
- "Add abs at the end of every workout"

Guardrails:
- Must still use exercises from database
- Must follow programming principles
- Cannot override safety rules (age/experience adaptations)
- Cannot request impossible combinations
"""
from typing import Dict, Any, List, Optional
import re


class ConstraintParser:
    """Parse and validate user-provided constraints"""
    
    # Valid equipment types that map to our database
    VALID_EQUIPMENT = {
        'barbell': 'barbell',
        'dumbbell': 'dumbbell', 
        'dumbbells': 'dumbbell',
        'cable': 'cable',
        'cables': 'cable',
        'machine': 'machine',
        'machines': 'machine',
        'bodyweight': 'bodyweight',
        'pull-up bar': 'bodyweight',
        'pull up bar': 'bodyweight',
        'pullup bar': 'bodyweight',
        'treadmill': 'cardio_equipment',
        'bike': 'cardio_equipment',
        'elliptical': 'cardio_equipment',
        'rowing machine': 'cardio_equipment',
        'bands': 'bands',
        'resistance bands': 'bands',
        'kettlebell': 'kettlebell',
        'kettlebells': 'kettlebell'
    }
    
    # Valid split types
    VALID_SPLITS = {
        'ppl': 'push_pull_legs',
        'push pull legs': 'push_pull_legs',
        'push/pull/legs': 'push_pull_legs',
        'upper lower': 'upper_lower',
        'upper/lower': 'upper_lower',
        'full body': 'full_body',
        'bro split': 'bro_split',
        'arnold': 'arnold_split',  # Special: PPL + chest/back + shoulders/arms
        'arnold split': 'arnold_split'
    }
    
    def __init__(self):
        """Initialize constraint parser"""
        pass
    
    def parse_constraints(self, user_input: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse user constraint input and return validated constraints.
        
        Strategy: Extract constraint CATEGORIES and pass raw text to OpenAI for interpretation.
        - Parser identifies: equipment, split, abs, cardio, other modifications
        - OpenAI interprets the nuance (e.g., "leg days" vs "every workout")
        - Guardrails only prevent unsafe combinations
        
        Args:
            user_input: Natural language constraint string from user
            user_profile: User's profile (for validation context)
            
        Returns:
            Dict with parsed constraints including raw text for OpenAI
        """
        constraints = {
            'raw_text': user_input.strip(),  # Pass full text to OpenAI
            'equipment_access': 'full_gym',  # Default
            'custom_split': None,
            'specific_equipment': [],
            'has_abs_request': False,
            'has_cardio_request': False,
            'warnings': [],
            'modifications': []
        }
        
        if not user_input or user_input.strip() == '':
            return constraints
        
        user_input_lower = user_input.lower().strip()
        
        # Parse equipment constraints (for database filtering)
        equipment_result = self._parse_equipment(user_input_lower)
        if equipment_result['found']:
            constraints['equipment_access'] = equipment_result['equipment_type']
            constraints['specific_equipment'] = equipment_result['equipment_list']
            constraints['modifications'].append(
                f"Equipment limited to: {', '.join(equipment_result['equipment_list'])}"
            )
        
        # Parse split type modifications (for guardrail validation)
        split_result = self._parse_split(user_input_lower, user_profile)
        if split_result['found']:
            if split_result['valid']:
                constraints['custom_split'] = split_result['split_type']
                constraints['modifications'].append(
                    f"Custom split: {split_result['split_type']}"
                )
            else:
                constraints['warnings'].append(split_result['reason'])
        
        # Detect abs/cardio mentions (OpenAI will interpret the details)
        if 'abs' in user_input_lower or 'core' in user_input_lower:
            constraints['has_abs_request'] = True
            constraints['modifications'].append("Abs/core modification requested")
        
        if 'cardio' in user_input_lower:
            constraints['has_cardio_request'] = True
            constraints['modifications'].append("Cardio modification requested")
        
        # Validate constraints don't conflict with safety guardrails
        validation = self._validate_constraints(constraints, user_profile)
        if not validation['valid']:
            constraints['warnings'].extend(validation['warnings'])
        
        return constraints
    
    def _parse_equipment(self, text: str) -> Dict[str, Any]:
        """Parse equipment constraints from text"""
        result = {
            'found': False,
            'equipment_type': 'full_gym',
            'equipment_list': []
        }
        
        # Keywords indicating limited equipment
        limited_keywords = [
            'only have', 'just have', 'limited to', 'only', 'just',
            'home gym', 'at home', 'no gym'
        ]
        
        has_limited = any(keyword in text for keyword in limited_keywords)
        
        if has_limited:
            # Extract equipment mentioned
            found_equipment = set()
            for equipment_name, db_type in self.VALID_EQUIPMENT.items():
                if equipment_name in text:
                    found_equipment.add(db_type)
            
            if found_equipment:
                result['found'] = True
                result['equipment_list'] = sorted(list(found_equipment))
                
                # Map to our equipment_access categories
                if found_equipment == {'bodyweight'}:
                    result['equipment_type'] = 'bodyweight_only'
                elif found_equipment == {'dumbbell'} or found_equipment == {'dumbbell', 'bodyweight'}:
                    result['equipment_type'] = 'dumbbells_only'
                elif 'barbell' not in found_equipment and 'machine' not in found_equipment:
                    result['equipment_type'] = 'home_gym'
                else:
                    result['equipment_type'] = 'full_gym'
        
        return result
    
    def _parse_split(self, text: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Parse custom split requests"""
        result = {
            'found': False,
            'valid': False,
            'split_type': None,
            'reason': ''
        }
        
        # Check if user mentions a split
        for split_name, split_type in self.VALID_SPLITS.items():
            if split_name in text:
                result['found'] = True
                result['split_type'] = split_type
                
                # Validate based on goal
                goal = user_profile.get('goal', 'general_fitness')
                days = user_profile.get('days_per_week', 4)
                
                # Validate arnold split (6 days required)
                if split_type == 'arnold_split':
                    if days < 6:
                        result['valid'] = False
                        result['reason'] = "Arnold split requires 6 days per week"
                    elif goal in ['weight_loss', 'general_fitness']:
                        result['valid'] = False
                        result['reason'] = "Arnold split only valid for strength/hypertrophy goals"
                    else:
                        result['valid'] = True
                
                # Other splits: follow existing goal rules
                elif goal in ['weight_loss', 'general_fitness']:
                    if split_type != 'full_body':
                        result['valid'] = False
                        result['reason'] = f"{goal} goals must use full body split (override not allowed)"
                    else:
                        result['valid'] = True
                else:
                    result['valid'] = True
                
                break
        
        return result
    
    def _parse_abs_cardio(self, text: str, feature: str) -> Dict[str, Any]:
        """
        Parse abs or cardio requests with context understanding.
        Can detect if user wants it on all days or specific days.
        
        Args:
            text: User input text (lowercased)
            feature: 'abs' or 'cardio'
            
        Returns:
            Dict with 'add_all' (bool) and 'specific_days' (list)
        """
        result = {
            'add_all': False,
            'specific_days': []
        }
        
        # Check if feature is mentioned at all
        if feature not in text:
            return result
        
        # Keywords that indicate ALL days
        all_keywords = ['every', 'all', 'each']
        
        # Keywords that indicate SPECIFIC days
        day_keywords = {
            'leg': ['leg day', 'leg days', 'legs day', 'legs'],
            'push': ['push day', 'push days', 'push'],
            'pull': ['pull day', 'pull days', 'pull'],
            'upper': ['upper day', 'upper days', 'upper body', 'upper'],
            'lower': ['lower day', 'lower days', 'lower body', 'lower'],
            'chest': ['chest day', 'chest days', 'chest'],
            'back': ['back day', 'back days', 'back'],
            'shoulders': ['shoulder day', 'shoulders day', 'shoulders', 'shoulder'],
            'arms': ['arm day', 'arms day', 'arms', 'arm']
        }
        
        # Check if user mentions specific days
        found_specific_days = []
        for day_type, keywords in day_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_specific_days.append(day_type)
        
        # Determine if all days or specific
        if found_specific_days:
            # User specified specific days (e.g., "abs at end of leg days")
            result['specific_days'] = found_specific_days
        elif any(keyword in text for keyword in all_keywords):
            # User said "every workout" or "all sessions"
            result['add_all'] = True
        else:
            # Ambiguous - mentioned abs/cardio but not clear where
            # Default to specific context clues
            # Check proximity: "abs at end" + "leg" nearby
            if 'at end' in text or 'after' in text or 'finish with' in text:
                # They want to add it somewhere, but didn't specify - default to all
                result['add_all'] = True
        
        return result
    
    def _validate_constraints(self, constraints: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate constraints don't conflict with safety rules"""
        validation = {
            'valid': True,
            'warnings': []
        }
        
        age = user_profile.get('age', 30)
        experience = user_profile.get('experience', 'intermediate')
        
        # Check if equipment is too limited for goal
        equipment = constraints['equipment_access']
        goal = user_profile.get('goal')
        
        if equipment == 'bodyweight_only' and goal == 'strength':
            validation['warnings'].append(
                "Bodyweight only may limit strength progression - consider adding resistance"
            )
        
        # Check if older beginner is trying advanced splits
        if age >= 55 and experience == 'beginner':
            if constraints['custom_split'] in ['arnold_split', 'bro_split']:
                validation['valid'] = False
                validation['warnings'].append(
                    "Advanced splits not recommended for older beginners - using full body for safety"
                )
                constraints['custom_split'] = 'full_body'
        
        return validation
    
    def format_constraints_for_openai(self, constraints: Dict[str, Any]) -> str:
        """
        Format parsed constraints into OpenAI prompt addition.
        
        Strategy: Pass user's raw text to OpenAI for interpretation, with guardrails.
        - OpenAI interprets nuance (e.g., "abs at end of leg days" vs "every workout")
        - Guardrails ensure safety and database compliance
        """
        
        raw_text = constraints.get('raw_text', '').strip()
        
        # If no constraints, return empty
        if not raw_text and not any([
            constraints.get('custom_split'),
            constraints.get('specific_equipment')
        ]):
            return ""
        
        prompt_addition = "\n\nUSER-SPECIFIED CONSTRAINTS:\n"
        
        # Equipment constraints (affects database filtering)
        if constraints.get('specific_equipment'):
            prompt_addition += f"- Available equipment: {', '.join(constraints['specific_equipment'])}\n"
            prompt_addition += "  * ONLY select exercises that use this equipment from the allowed list\n"
        
        # Split type constraints (validated by guardrails)
        if constraints.get('custom_split'):
            split_type = constraints['custom_split']
            if split_type == 'arnold_split':
                prompt_addition += "- Split: Arnold Split (6 days)\n"
                prompt_addition += "  * Day 1: Chest\n"
                prompt_addition += "  * Day 2: Back\n"
                prompt_addition += "  * Day 3: Legs\n"
                prompt_addition += "  * Day 4: Chest + Back\n"
                prompt_addition += "  * Day 5: Shoulders + Arms\n"
                prompt_addition += "  * Day 6: Legs\n"
            else:
                prompt_addition += f"- Use {split_type} split as specified\n"
        
        # USER'S RAW REQUEST - Let OpenAI interpret
        if raw_text:
            prompt_addition += f"\nUser's modification request: \"{raw_text}\"\n"
            prompt_addition += "Please interpret and implement this request intelligently:\n"
            
            if constraints.get('has_abs_request'):
                prompt_addition += "  * User wants abs/core modifications - understand the context:\n"
                prompt_addition += "    - 'abs at end of leg days' = add abs exercises to ALL leg day sessions (not just one)\n"
                prompt_addition += "    - 'abs every workout' = add abs to EVERY workout session\n"
                prompt_addition += "    - 'abs on upper body days' = add abs to ALL upper body sessions\n"
                prompt_addition += "    - When user specifies certain day types, apply to ALL sessions of that type\n"
            
            if constraints.get('has_cardio_request'):
                prompt_addition += "  * User wants cardio modifications - understand the context:\n"
                prompt_addition += "    - 'cardio after push days' = add cardio to ALL push day sessions\n"
                prompt_addition += "    - 'cardio every session' = add cardio to ALL workout sessions\n"
                prompt_addition += "    - When user specifies certain day types, apply to ALL sessions of that type\n"
                prompt_addition += "    - Duration: 15-25 minutes based on goal and experience\n"
        
        # GUARDRAILS
        prompt_addition += "\nIMPORTANT GUARDRAILS (non-negotiable):\n"
        prompt_addition += "- Still respect age/experience exercise selection rules\n"
        prompt_addition += "- ONLY use exercises from allowed_exercises list provided\n"
        prompt_addition += "- If user's request conflicts with safety, prioritize safety\n"
        prompt_addition += "- User requests are modifications, not complete overrides\n"
        
        return prompt_addition
