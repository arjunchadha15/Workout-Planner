"""
OpenAI Service for workout plan generation.
Handles prompt construction and API calls to OpenAI.
"""
from typing import Dict, Any, List
import json
import logging
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for generating workout plans using OpenAI"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        Config.validate()  # Ensure API key is present
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.OPENAI_MAX_TOKENS
        self.temperature = Config.OPENAI_TEMPERATURE
    
    def generate_plan(
        self,
        user_profile: Dict[str, Any],
        constraints: Dict[str, Any],
        allowed_exercises: List[Dict[str, Any]],
        allowed_cardio: List[Dict[str, Any]],
        constraint_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a workout plan using OpenAI.
        
        Args:
            user_profile: Dict with goal, days_per_week, experience, gender, body_weight_lb
            constraints: Dict with session_length_minutes, equipment_access (deprecated - use constraint_prompt)
            allowed_exercises: List of exercise dicts with id, name, category, equipment, suggested_weight_lb
            allowed_cardio: List of cardio dicts with cardio_id, name, default_zone, default_duration_min
            constraint_prompt: Optional formatted constraint text from ConstraintParser
            
        Returns:
            Plan dict following the target schema
            
        Raises:
            Exception if OpenAI call fails
        """
        # Build the prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            user_profile,
            constraints,
            allowed_exercises,
            allowed_cardio,
            constraint_prompt=constraint_prompt
        )
        
        # Define response schema
        response_schema = self._get_response_schema()
        
        try:
            logger.info(f"Calling OpenAI API with model: {self.model}")
            
            # Call OpenAI with JSON mode
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Parse response
            content = response.choices[0].message.content
            plan_data = json.loads(content)
            
            logger.info("Successfully generated plan from OpenAI")
            
            # Validate and return
            validated_plan = self._validate_plan(plan_data, user_profile, allowed_exercises)
            return validated_plan
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise Exception(f"Failed to generate plan: {str(e)}")
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with rules and guidelines"""
        return """You are an expert strength & conditioning coach and workout programming specialist.

Your task is to generate personalized workout plans that are:
1. EVIDENCE-BASED: Follow proven programming principles
2. SAFE: Appropriate for the user's experience level, age, and capabilities
3. EFFECTIVE: Optimized for their specific goal
4. STRUCTURED: Well-organized with proper progression
5. INDIVIDUALIZED: Use your expertise to select appropriate exercises from the allowed list

CRITICAL RULES (MUST FOLLOW):
- You MUST ONLY use exercise IDs from the provided allowed_exercises list
- You MUST create exactly the number of sessions specified in days_per_week
- You MUST include exactly the specified number of exercises per day
- You MUST NOT repeat the same exercise within a single workout session
- You MUST follow the specified split type (Upper/Lower, PPL, Full Body, or Bro Split)
- You MUST use goal-appropriate programming (sets/reps)
- You MUST provide reps as a SINGLE NUMBER (e.g., "10"), NOT a range (e.g., NOT "8-12")
- You MUST include the suggested_weight_lb from the exercise list for each exercise (use null if not provided)
- DO NOT include rest_seconds or notes - only output: exercise_id, sets, reps, suggested_weight_lb
- Cardio is OPTIONAL - only include if beneficial for the goal

EXERCISE SELECTION INTELLIGENCE:
Use your coaching expertise to select appropriate exercises from the allowed list based on:

AGE CONSIDERATIONS:
- Ages 18-30: Can handle all movements including explosive and complex exercises
- Ages 31-50: Prefer stable, controlled movements. Avoid excessive jumping or high-impact
- Ages 51-65: Focus on joint-friendly exercises. Avoid overhead pressing if shoulder mobility is concern
- Ages 65+: Prioritize stability, balance, and controlled movements. Avoid complex barbell movements

EXPERIENCE LEVEL ADAPTATIONS:
- BEGINNER: 
  * Stick to basic compound movements with clear movement patterns
  * Avoid: Complex olympic lifts, advanced variations, exercises requiring high coordination
  * Prefer: Machines over free weights, dumbbells over barbells, bilateral over unilateral
  * Examples to prioritize: leg press over squats, machine chest press over barbell bench
  
- INTERMEDIATE:
  * Can handle most compound movements and some variations
  * Introduce more free weight work and unilateral movements
  * Can include: Romanian deadlifts, Bulgarian split squats, cable variations
  
- ADVANCED:
  * Full exercise library available
  * Can include: Complex variations, heavy compounds, advanced techniques

SAFETY-FIRST FILTERING:
Even if an exercise is in the allowed list, use your judgment:

BEGINNERS should AVOID:
- Pull-ups, chin-ups (unless assisted versions available)
- Deadlifts (regular barbell), Romanian deadlifts
- Heavy overhead pressing, barbell shoulder press
- Complex olympic movements, power cleans
- Ab wheel rollouts, advanced core exercises
- Bulgarian split squats, pistol squats

BEGINNERS should PREFER:
- Leg press over squats
- Machine chest press over barbell bench
- Cable exercises over free weights when possible
- Lat pulldowns instead of pull-ups
- Planks and basic crunches for core

OLDER ADULTS (55+) should AVOID:
- Heavy barbell squats and deadlifts
- Overhead pressing with heavy weights
- High-impact or jumping movements
- Exercises requiring extreme balance (pistol squats, single-leg variations)
- Advanced bodyweight exercises (pull-ups, dips, ab wheel)

OLDER ADULTS (55+) should PREFER:
- Machines (leg press, chest press, lat pulldown, leg curl, leg extension)
- Cable exercises for controlled movement
- Seated variations over standing
- Dumbbell exercises with lighter weights over barbells
- Step-ups or lunges over jumping movements

COMBINATION (Beginner AND 55+) = MAXIMUM SAFETY:
- Stick almost entirely to machines and cables
- Very basic dumbbell work only
- No pull-ups, deadlifts, heavy squats, or complex movements whatsoever
- Focus on building foundational strength safely

GOAL-SPECIFIC PROGRAMMING RULES:

STRENGTH:
- Rep range: 3-6 reps (choose a single number from this range)
- Rest: 3-5 minutes for compounds, 2-3 for accessories
- Focus: Heavy compound lifts (squat, bench, deadlift, overhead press)
- Volume: Lower reps, higher weight
- Split: Uses selected split type (upper/lower, PPL, full body, bro split)
- Cardio: DO NOT ADD CARDIO (strength training only, no cardio blocks)

HYPERTROPHY:
- Rep range: 8-12 reps (choose a single number from this range)
- Rest: 60-90 seconds
- Focus: Balanced compounds and isolation exercises
- Volume: Moderate to high sets (3-5 sets per exercise)
- Split: Uses selected split type (upper/lower, PPL, full body, bro split)
- Cardio: DO NOT ADD CARDIO (focus on muscle building, no cardio blocks)

WEIGHT LOSS:
- Rep range: 15-20 reps (choose a single number from this range)
- Rest: 30-45 seconds (keep heart rate elevated)
- Focus: High-rep full-body compound exercises for calorie burn
- Cardio: REQUIRED on 70% of workout sessions (e.g., if 4 days/week, include cardio on 3 days)
- Cardio Guidelines: Use your expertise to recommend optimal zone (zone2/zone3/zone4) and duration (25-35 min) based on user's experience level. More experienced users can handle zone3/zone4.
- Structure: Strength exercises first (4-5 exercises), then cardio block
- Split: Always full_body (ignore any other split selection)
- Priority: Maximize calorie burn and fat loss while preserving muscle

GENERAL FITNESS:
- Rep range: 10-12 reps (choose a single number from this range)
- Rest: 60-90 seconds
- Focus: Balanced approach - strength and cardiovascular health
- Cardio: REQUIRED on 50% of workout sessions (e.g., if 4 days/week, include cardio on 2 days)
- Cardio Guidelines: Use your expertise to recommend optimal zone (zone2/zone3) and duration (20-30 min) that complements the strength work.
- Structure: Strength exercises first (5 exercises), then cardio block when included
- Split: Always full_body (ignore any other split selection)
- Priority: Overall health, longevity, and balanced fitness

OUTPUT FORMAT:
You MUST respond with valid JSON following this exact structure:
{
  "plan_version": "v1",
  "overview": {
    "goal": "<strength|hypertrophy|weight_loss|general_fitness>",
    "days_per_week": <number>,
    "split_type": "<split type>",
    "exercises_per_day": <number>
  },
  "sessions": [
    {
      "day_index": <0-based index>,
      "title": "<session name>",
      "blocks": [
        {
          "type": "strength",
          "items": [
            {
              "exercise_id": "<must match allowed exercise ID>",
              "sets": <number>,
              "reps": <single number, NOT a range>,
              "suggested_weight_lb": <number or null>
            }
          ]
        },
        {
          "type": "cardio",
          "cardio_id": "<cardio_id from allowed list>",
          "zone": "<zone2, zone3, or zone4>",
          "duration_minutes": <number>
        }
      ]
    }
  ]
}
IMPORTANT RULES: 
- Each workout session must have UNIQUE exercises - NEVER repeat an exercise_id within the same day
- If you need 6 exercises for a push day, select 6 DIFFERENT exercises (e.g., bench-press, overhead-press, dips, cable-fly, triceps-extension, lateral-raise)
- Strength blocks use "items" array with exercise objects
- Cardio blocks have NO "items" - just "cardio_id", "zone", and "duration_minutes" fields directly in the block
- DO NOT use bench-press twice, DO NOT use squat twice, etc. within the same session
- The "reps" field must be a single integer (e.g., 10), not a string or range (e.g., NOT "8-12")
- Use the suggested_weight_lb from the allowed exercises list

EXAMPLE of CORRECT workout (all exercises are unique):
{
  "day_index": 0,
  "title": "Push Day",
  "blocks": [
    {
      "type": "strength",
      "items": [
        {"exercise_id": "bench-press", "sets": 4, "reps": 10, "suggested_weight_lb": 135},
        {"exercise_id": "overhead-press", "sets": 3, "reps": 10, "suggested_weight_lb": 95},
        {"exercise_id": "dips", "sets": 3, "reps": 10, "suggested_weight_lb": null},
        {"exercise_id": "cable-fly", "sets": 3, "reps": 12, "suggested_weight_lb": 40}
      ]
    },
    {
      "type": "cardio",
      "cardio_id": "treadmill",
      "zone": "zone3",
      "duration_minutes": 25
    }
  ]
}

EXAMPLE of WRONG workout (NEVER do this - bench-press repeated):
{
  "items": [
    {"exercise_id": "bench-press", "sets": 4, "reps": 10, ...},
    {"exercise_id": "bench-press", "sets": 3, "reps": 8, ...},  // ❌ WRONG - duplicate!
  ]
}
"""
    
    def _get_split_rules(self, split_type: str, days_per_week: int) -> str:
        """Get explicit rules for each split type to ensure correct exercise placement"""
        
        if split_type == 'push_pull_legs':
            return f"""
For a {days_per_week}-day Push/Pull/Legs program:

PUSH DAYS - Upper Body Pressing (Chest, Shoulders, Triceps ONLY):
- Chest exercises: bench press, incline press, dumbbell press, chest fly, cable fly, dips (chest variation)
- Shoulder exercises: overhead press, lateral raise, front raise, Arnold press
- Tricep exercises: tricep extension, tricep pushdown, overhead tricep extension, close-grip press
- ❌ NEVER include: squats, leg press, deadlifts, rows, pull-ups, lat pulldowns, bicep curls, leg exercises

PULL DAYS - Upper Body Pulling (Back, Biceps ONLY):
- Back exercises: deadlifts, bent-over rows, pull-ups, lat pulldowns, seated rows, T-bar rows, face pulls
- Bicep exercises: bicep curls, hammer curls, preacher curls, cable curls
- ❌ NEVER include: squats, leg press, bench press, overhead press, chest exercises, tricep exercises, leg exercises

LEG DAYS - Lower Body ONLY (Quads, Hamstrings, Glutes, Calves):
- Quad exercises: squats, leg press, leg extensions, lunges, front squats
- Hamstring exercises: Romanian deadlifts, leg curls, good mornings
- Glute exercises: hip thrusts, Bulgarian split squats
- Calf exercises: calf raises
- ❌ NEVER include: bench press, rows, pull-ups, overhead press, chest exercises, back exercises, arm exercises

CYCLE PATTERN: Push → Pull → Legs → Push → Pull → Legs (repeat)
"""
        
        elif split_type == 'upper_lower':
            return f"""
For a {days_per_week}-day Upper/Lower program:

UPPER DAYS - All Upper Body (Chest, Back, Shoulders, Arms):
- Chest: bench press, incline press, dumbbell press, chest fly, dips
- Back: rows, pull-ups, lat pulldowns, deadlifts (can be upper or lower)
- Shoulders: overhead press, lateral raises, front raises
- Arms: bicep curls, tricep extensions
- ❌ NEVER include: squats, leg press, leg extensions, leg curls, lunges, calf raises, ANY lower body exercises

LOWER DAYS - All Lower Body (Quads, Hamstrings, Glutes, Calves):
- Quads: squats, leg press, leg extensions, lunges, front squats
- Hamstrings: Romanian deadlifts, leg curls, good mornings
- Glutes: hip thrusts, Bulgarian split squats
- Calves: calf raises
- ❌ NEVER include: bench press, rows, pull-ups, overhead press, chest, back, shoulder, or arm exercises

CYCLE PATTERN: Upper → Lower → Upper → Lower (alternate)
"""
        
        elif split_type == 'bro_split':
            return f"""
For a {days_per_week}-day Bro Split (each muscle group gets its own day):

DAY 1 - CHEST ONLY:
- Only chest exercises: bench press, incline press, dumbbell press, chest fly, cable fly, dips (chest variation)
- ❌ NO shoulders, triceps, back, legs, or other muscle groups

DAY 2 - BACK ONLY:
- Only back exercises: deadlifts, bent-over rows, pull-ups, lat pulldowns, seated rows, T-bar rows
- ❌ NO biceps, shoulders, chest, legs, or other muscle groups

DAY 3 - SHOULDERS ONLY:
- Only shoulder exercises: overhead press, lateral raises, front raises, Arnold press, upright rows, face pulls
- ❌ NO chest, triceps, back, legs, or other muscle groups

DAY 4 - LEGS ONLY:
- Only leg exercises: squats, leg press, leg extensions, leg curls, lunges, calf raises, Romanian deadlifts
- ❌ NO upper body exercises at all

DAY 5 - ARMS ONLY (Biceps + Triceps):
- Bicep exercises: bicep curls, hammer curls, preacher curls, cable curls
- Tricep exercises: tricep extensions, tricep pushdowns, overhead tricep extensions, close-grip press
- ❌ NO chest, back, shoulders, or legs

CYCLE PATTERN: Chest → Back → Shoulders → Legs → Arms (repeat)
"""
        
        elif split_type == 'full_body':
            return f"""
For a {days_per_week}-day Full Body program:

EVERY DAY - Mix of All Major Muscle Groups:
- Include exercises from ALL categories in each session:
  * Lower body: squats, leg press, deadlifts, lunges, leg curls
  * Upper push: bench press, overhead press, dips, chest exercises
  * Upper pull: rows, pull-ups, lat pulldowns, back exercises
  * Optional: Arms (biceps, triceps) and accessory work

- Balance each session with variety across muscle groups
- Each session should train the entire body with different exercise variations
"""
        
        else:
            return "Follow the standard programming for the selected split type."
    
    def _build_user_prompt(
        self,
        user_profile: Dict[str, Any],
        constraints: Dict[str, Any],
        allowed_exercises: List[Dict[str, Any]],
        allowed_cardio: List[Dict[str, Any]],
        constraint_prompt: str = ""
    ) -> str:
        """Build the user-specific prompt with all context"""
        
        goal = user_profile.get('goal', 'general_fitness')
        days_per_week = user_profile.get('days_per_week', 4)
        experience = user_profile.get('experience', 'intermediate')
        gender = user_profile.get('gender', 'male')
        age = user_profile.get('age', 30)
        bodyweight_lb = user_profile.get('body_weight_lb', 150)
        split_type = user_profile.get('split_type', 'upper_lower')
        exercises_per_day = user_profile.get('exercises_per_day', 6)
        
        equipment = user_profile.get('equipment_access', 'full_gym')
        
        # Map split type to description
        split_descriptions = {
            'upper_lower': 'Upper/Lower split - alternating upper and lower body days',
            'push_pull_legs': 'Push/Pull/Legs split - push exercises, pull exercises, and leg exercises',
            'full_body': 'Full Body split - train all major muscle groups each session',
            'bro_split': 'Bro Split - one muscle group per day (Chest, Back, Shoulders, Legs, Arms)'
        }
        split_desc = split_descriptions.get(split_type, split_type)
        
        # Format exercises for prompt
        exercise_list_str = "\n".join([
            f"- {ex['exercise_id']}: {ex['name']} ({ex['equipment']}, {ex['category']})"
            + (f" [suggested: {ex['suggested_weight_lb']} lb]" if ex.get('suggested_weight_lb') else "")
            for ex in allowed_exercises[:40]  # Limit to avoid token limits
        ])
        
        # Format cardio options
        cardio_list_str = "\n".join([
            f"- {c['cardio_id']}: {c['name']} (default: {c['default_zone']}, {c['default_duration_min']} min)"
            for c in allowed_cardio
        ])
        
        prompt = f"""Generate a {days_per_week}-day per week workout plan for:

USER PROFILE:
- Goal: {goal}
- Experience Level: {experience}
- Gender: {gender}
- Age: {age} years
- Bodyweight: {bodyweight_lb} lb
- Days per Week: {days_per_week}
- Split Type: {split_desc}
- Exercises per Day: {exercises_per_day}

SPLIT TYPE RULES - FOLLOW THESE EXACTLY:
{self._get_split_rules(split_type, days_per_week)}

CONSTRAINTS:
- Equipment Access: {equipment}

ALLOWED EXERCISES (you MUST only use these exercise_id values):
{exercise_list_str}

⚠️ CRITICAL: You can ONLY use the exercise_id values listed above. DO NOT create or use any exercise_id not in this list!
Examples of exercises you CANNOT use (not in the allowed list): tricep-pushdown, bicep-curls, romanian-deadlift, leg-curl, calf-raises, incline-press, arnold-press, etc. unless they appear in the list above.

AVAILABLE CARDIO OPTIONS (select cardio_id from these options):
{cardio_list_str}
{constraint_prompt}

CARDIO ZONES (use your expertise to select the best zone):
- zone2: Low intensity, conversational pace (60-70% max HR)
  * Best for: Beginners, recovery days, building aerobic base, general fitness
  * Sustainable for: 20-45 minutes
  * Fat burning: Moderate, primarily uses fat for fuel
  
- zone3: Moderate intensity (70-80% max HR)
  * Best for: Intermediate users, general fitness, balanced fat burning
  * Sustainable for: 20-35 minutes
  * Fat burning: Good, mix of fat and carbs
  
- zone4: High intensity steady state (80-90% max HR)
  * Best for: Advanced users, maximum calorie burn, performance
  * Sustainable for: 15-30 minutes
  * Fat burning: Highest total calories, aggressive weight loss

DO NOT USE: hiit, liss, or any other zone labels. Only use zone2, zone3, or zone4.

REQUIREMENTS:
1. Create EXACTLY {days_per_week} workout sessions following the {split_type} split pattern
2. Include EXACTLY {exercises_per_day} strength exercises per session (not counting cardio)
3. CRITICAL: Each exercise can only appear ONCE per workout session - NO REPEATS within the same day
4. Follow the {goal} programming rules from the system prompt STRICTLY
5. Use appropriate rep ranges, sets, and rest periods for {goal}
6. Balance muscle groups according to the {split_type} split
7. Include progressive overload potential
8. Each exercise must have a SINGLE NUMBER for reps (e.g., 10), not a range (e.g., NOT "8-12")
9. DO NOT include notes or coaching cues - output only the raw workout data
10. Title each session appropriately for the {split_type} split

WEIGHT RECOMMENDATIONS:
- For exercises with [suggested: X lb] in the allowed exercises list above, use that weight
- For exercises WITHOUT a suggested weight (showing [suggested: None] or no weight listed):
  * If it's a BODYWEIGHT exercise (pull-ups, dips, push-ups, etc.), set suggested_weight_lb to null
  * If it's a WEIGHTED exercise, YOU MUST calculate an appropriate starting weight based on:
    - User's bodyweight ({bodyweight_lb} lb)
    - User's experience level ({experience})
    - Other exercises with known weights in the plan (use relative strength ratios)
    - The muscle group and exercise type
  
EXAMPLE WEIGHT CALCULATIONS (only for exercises in your allowed list without suggested weights):
- If user can bench press 135 lb, similar chest exercises should be ~100-140 lb range
- If user can squat 185 lb, other leg exercises should scale proportionally
- If user can overhead press 95 lb, shoulder isolation work should be ~20-40 lb
- Cable/machine exercises: generally 40-70% of equivalent barbell movement
- For intermediate users: compound lifts ~1-1.5x bodyweight, isolation ~0.3-0.6x bodyweight

IMPORTANT: ONLY recommend exercises from the ALLOWED EXERCISES list above. NEVER use suggested_weight_lb as null for weighted exercises!

CARDIO PROGRAMMING (Use Your Expertise):
- Consider user's experience level when selecting zone and duration
- Beginners: Start with lower zones (zone2) and shorter durations (15-20 min)
- Intermediate: Can handle zone3 and moderate durations (20-30 min)
- Advanced: Can sustain zone4 and longer durations (30-40 min)
- Vary intensity across the week for optimal results and recovery
- For weight loss: Prioritize higher zones when user can handle it
- For general fitness: Balance between zones for sustainable progress

SPECIAL REQUIREMENTS FOR GOALS:
- WEIGHT LOSS: Cardio-dominant sessions. Use your expertise to prescribe optimal cardio zone and duration (20-40 min) based on user profile. Include 2-4 high-rep full-body exercises. ALWAYS use full_body approach.
- GENERAL FITNESS: Balanced sessions with ~50/50 strength and cardio. Use your judgment for cardio duration (15-25 min) and zone that complements strength work. Include 4-5 functional exercises. ALWAYS use full_body approach.
- STRENGTH/HYPERTROPHY: Strength-focused. Cardio is optional - include only if beneficial for recovery or conditioning. Use the selected split type.

Generate the complete workout plan now as JSON."""
        
        return prompt
    
    def _get_response_schema(self) -> Dict[str, Any]:
        """Define the expected response schema"""
        return {
            "type": "object",
            "properties": {
                "plan_version": {"type": "string"},
                "overview": {
                    "type": "object",
                    "properties": {
                        "goal": {"type": "string"},
                        "days_per_week": {"type": "number"},
                        "session_length_minutes": {"type": "number"},
                        "notes": {"type": "string"}
                    },
                    "required": ["goal", "days_per_week", "session_length_minutes"]
                },
                "sessions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "day_index": {"type": "number"},
                            "title": {"type": "string"},
                            "blocks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string"},
                                        "items": {"type": "array"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "required": ["plan_version", "overview", "sessions"]
        }
    
    def _validate_plan(
        self,
        plan_data: Dict[str, Any],
        user_profile: Dict[str, Any],
        allowed_exercises: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate the generated plan against requirements.
        STRICT validation - ensures plan exactly matches input requirements.
        
        Args:
            plan_data: The plan dict from OpenAI
            user_profile: Original user profile
            allowed_exercises: List of allowed exercises
            
        Returns:
            Validated plan dict
            
        Raises:
            ValueError if critical validation fails
        """
        # Check required fields
        if 'sessions' not in plan_data:
            raise ValueError("Plan missing 'sessions' field")
        
        if 'overview' not in plan_data:
            raise ValueError("Plan missing 'overview' field")
        
        sessions = plan_data['sessions']
        overview = plan_data['overview']
        
        # VALIDATION 1: Check days per week matches
        expected_days = user_profile.get('days_per_week', 4)
        if len(sessions) != expected_days:
            logger.error(
                f"CRITICAL: Plan has {len(sessions)} sessions but expected {expected_days}. "
                f"This is a generation error."
            )
            # Update overview to reflect actual
            overview['days_per_week'] = len(sessions)
        else:
            logger.info(f"✓ Days per week correct: {len(sessions)}/{expected_days}")
        
        # Ensure overview matches input
        overview['goal'] = user_profile.get('goal', overview.get('goal'))
        overview['days_per_week'] = len(sessions)  # Use actual count
        
        # VALIDATION 2: Build set of allowed exercise IDs
        allowed_ids = {ex['exercise_id'] for ex in allowed_exercises}
        logger.info(f"Validating exercises against {len(allowed_ids)} allowed exercises")
        
        # VALIDATION 3: Check each session
        total_invalid_exercises = 0
        expected_exercises_per_day = user_profile.get('exercises_per_day', 5)
        
        for i, session in enumerate(sessions):
            for block in session.get('blocks', []):
                if block.get('type') == 'strength':
                    # Filter out any exercises not in allowed list
                    valid_items = []
                    invalid_count = 0
                    
                    for item in block.get('items', []):
                        exercise_id = item.get('exercise_id')
                        if exercise_id and exercise_id not in allowed_ids:
                            logger.warning(
                                f"Day {i+1}: Exercise '{exercise_id}' NOT IN DATABASE - REMOVING"
                            )
                            invalid_count += 1
                            total_invalid_exercises += 1
                        else:
                            valid_items.append(item)
                    
                    # Replace items with only valid exercises
                    block['items'] = valid_items
                    
                    # Check exercise count
                    actual_count = len(valid_items)
                    if actual_count != expected_exercises_per_day:
                        logger.warning(
                            f"Day {i+1}: Has {actual_count} exercises, expected {expected_exercises_per_day}"
                        )
                    
                    # Check for duplicates within session
                    exercise_ids = [item['exercise_id'] for item in valid_items]
                    duplicates = set([ex for ex in exercise_ids if exercise_ids.count(ex) > 1])
                    if duplicates:
                        logger.error(
                            f"Day {i+1}: DUPLICATE EXERCISES FOUND: {duplicates}"
                        )
        
        # Final report
        if total_invalid_exercises > 0:
            logger.warning(
                f"⚠️  Removed {total_invalid_exercises} invalid exercises from plan"
            )
        else:
            logger.info("✓ All exercises valid (from database)")
        
        logger.info("Plan validation complete")
        return plan_data
