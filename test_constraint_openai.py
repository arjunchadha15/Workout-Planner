"""
Test constraint parser with OpenAI integration
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

# Check which days have abs
abs_keywords = ['ab', 'core', 'crunch', 'plank', 'sit-up', 'leg-raise']
for i, session in enumerate(plan['sessions'], 1):
    has_abs = False
    abs_exercises = []
    for block in session['blocks']:
        if block['type'] == 'strength':
            for item in block['items']:
                exercise_id = item.get('exercise_id', '').lower()
                if any(keyword in exercise_id for keyword in abs_keywords):
                    has_abs = True
                    abs_exercises.append(item['exercise_id'])
    
    status = f"✅ Has abs: {', '.join(abs_exercises)}" if has_abs else "❌ No abs"
    print(f"Day {i}: {status}")

# Show first 3 sessions details
print()
print('First 3 sessions (detailed):')
for i, session in enumerate(plan['sessions'][:3], 1):
    print(f"\nDay {i}:")
    for block in session['blocks']:
        if block['type'] == 'strength':
            exercises = [item['exercise_id'] for item in block['items']]
            print(f"  Exercises: {', '.join(exercises)}")
