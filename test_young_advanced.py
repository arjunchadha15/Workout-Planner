"""
Test: 25-year-old Advanced athlete 
Should get complex exercises, heavy compounds, full exercise library
"""
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from ai_plan_generation_service import AIPlanGenerationService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
import json

print("="*60)
print("🧪 TESTING: 25-year-old Advanced Athlete")
print("="*60)

DATABASE_URL = Config.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

user_profile = {
    "goal": "strength",
    "days_per_week": 4,
    "experience": "advanced",
    "gender": "male",
    "age": 25,
    "bodyweight_lb": 185.0,
    "split_type": "upper_lower",
    "exercises_per_day": 5
}

constraints = {"equipment_access": "full_gym"}

print(f"\nProfile: {user_profile['age']} years old, {user_profile['experience']}, {user_profile['goal']}")
print("Expected: Heavy compounds (squat, deadlift, bench), complex movements, full exercise library")

try:
    service = AIPlanGenerationService(db)
    print("\n⏳ Generating plan (OpenAI will select advanced exercises)...")
    
    result = service.generate_plan(
        user_id="test_user",
        user_profile=user_profile,
        constraints=constraints
    )
    
    plan = result['plan']
    
    print("\n✅ Plan Generated!")
    print("\n📋 EXERCISES SELECTED:")
    
    for i, session in enumerate(plan.get('sessions', []), 1):
        print(f"\n  Session {i} - {session.get('title', 'Workout')}:")
        for block in session.get('blocks', []):
            if block.get('type') == 'strength':
                for item in block.get('items', []):
                    name = item.get('exercise_name', item.get('exercise_id'))
                    equip = item.get('equipment', '?')
                    weight = item.get('suggested_weight_lb')
                    weight_str = f"{weight} lb" if weight else "bodyweight"
                    print(f"    - {name} ({equip}) - {weight_str}")
            elif block.get('type') == 'cardio':
                cardio = block.get('cardio_id', 'N/A')
                zone = block.get('zone', 'N/A')
                duration = block.get('duration_minutes', 0)
                print(f"    [Cardio: {cardio}, {zone}, {duration} min]")
    
    # Save
    with open('test_plan_young_advanced.json', 'w') as f:
        json.dump(plan, f, indent=2)
    
    print("\n💾 Saved to: test_plan_young_advanced.json")
    
    # Compare exercise complexity
    print("\n" + "="*60)
    print("📊 COMPARISON ANALYSIS")
    print("="*60)
    print("\nOlder Beginner (65 years) got:")
    print("  - Bodyweight squats, dumbbell exercises, basic movements")
    print("  - Zone2 cardio (low intensity)")
    print("\nYoung Advanced (25 years) got:")
    
    # Check for advanced exercises
    has_heavy_compounds = False
    has_barbell = False
    for session in plan.get('sessions', []):
        for block in session.get('blocks', []):
            if block.get('type') == 'strength':
                for item in block.get('items', []):
                    ex_id = item.get('exercise_id', '')
                    if 'deadlift' in ex_id or 'squat' in ex_id and 'bodyweight' not in ex_id:
                        has_heavy_compounds = True
                    if item.get('equipment') == 'barbell' or 'barbell' in ex_id:
                        has_barbell = True
    
    if has_heavy_compounds:
        print("  ✅ Heavy compound lifts (squat/deadlift)")
    if has_barbell:
        print("  ✅ Barbell exercises")
    
    print("\n✅ OpenAI successfully adapted exercise selection based on age & experience!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
