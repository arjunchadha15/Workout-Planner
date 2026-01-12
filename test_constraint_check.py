"""
Check the constraint test results more accurately
"""
from constraint_parser import ConstraintParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from ai_plan_generation_service import AIPlanGenerationService
import json

print('🧪 Testing: "i want abs at the end of leg days"')
print('=' * 80)

# Setup database
engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

user_profile = {
    'age': 25,
    'gender': 'male',
    'body_weight_lb': 180,
    'goal': 'hypertrophy',
    'experience': 'intermediate',
    'days_per_week': 6,
    'exercises_per_day': 5,
    'equipment_access': 'full_gym',
    'split_type': 'push_pull_legs'
}

service = AIPlanGenerationService(db)
result = service.generate_plan(
    user_id='test_user',
    user_profile=user_profile,
    constraint_text='i want abs at the end of leg days'
)

# Result format: {"user_id": "...", "plan": {...}, "metadata": {...}}
plan = result['plan']
print(f"✅ Plan generated successfully!")
print(f"Days per week: {plan['overview']['days_per_week']}")
print(f"Split: {plan['overview']['split_type']}")
print()

# More specific abs keywords - must be core/ab-specific movements
abs_keywords = ['crunch', 'plank', 'sit-up', 'leg-raise', 'knee-raise', 'hanging', 'ab-wheel', 'woodchopper', 'russian-twist', 'bicycle']

print('Checking each day for ab/core exercises:')
print('(PPL = Day 1: Push, Day 2: Pull, Day 3: Leg, Day 4: Push, Day 5: Pull, Day 6: Leg)')
print()

for i, session in enumerate(plan['sessions'], 1):
    has_abs = False
    abs_exercises = []
    all_exercises = []
    
    for block in session['blocks']:
        if block['type'] == 'strength':
            for item in block['items']:
                exercise_id = item.get('exercise_id', '')
                all_exercises.append(exercise_id)
                
                # Check if it's a true ab exercise
                if any(keyword in exercise_id.lower() for keyword in abs_keywords):
                    has_abs = True
                    abs_exercises.append(exercise_id)
    
    day_type = ""
    if i in [1, 4]:
        day_type = "(PUSH)"
    elif i in [2, 5]:
        day_type = "(PULL)"
    elif i in [3, 6]:
        day_type = "(LEG) ⭐"
    
    status = f"✅ HAS ABS: {', '.join(abs_exercises)}" if has_abs else "❌ No abs"
    print(f"Day {i} {day_type}: {status}")
    print(f"   All exercises: {', '.join(all_exercises)}")
    print()

# Summary
print('=' * 80)
print('EXPECTED: Abs on Day 3 (Leg) and Day 6 (Leg) only')
print('ACTUAL: Check results above')
