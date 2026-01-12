"""
Quick test: Older beginner vs Young advanced to see exercise adaptation
"""
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from ai_plan_generation_service import AIPlanGenerationService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
import json

# Test older beginner - should get safer, simpler exercises
print("="*60)
print("🧪 TESTING: 65-year-old Beginner")
print("="*60)

DATABASE_URL = Config.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

user_profile = {
    "goal": "general_fitness",
    "days_per_week": 3,
    "experience": "beginner",
    "gender": "male",
    "age": 65,
    "bodyweight_lb": 160.0,
    "split_type": "full_body",
    "exercises_per_day": 4
}

constraints = {"equipment_access": "full_gym"}

print(f"\nProfile: {user_profile['age']} years old, {user_profile['experience']}, {user_profile['goal']}")
print("Expected: Machines, cable exercises, seated variations - NO heavy barbell compounds")

try:
    service = AIPlanGenerationService(db)
    print("\n⏳ Generating plan (OpenAI will select safe exercises)...")
    
    result = service.generate_plan(
        user_id="test_user",
        user_profile=user_profile,
        constraints=constraints
    )
    
    plan = result['plan']
    
    print("\n✅ Plan Generated!")
    print("\n📋 EXERCISES SELECTED:")
    
    for i, session in enumerate(plan.get('sessions', []), 1):
        print(f"\n  Session {i}:")
        for block in session.get('blocks', []):
            if block.get('type') == 'strength':
                for item in block.get('items', []):
                    name = item.get('exercise_name', item.get('exercise_id'))
                    equip = item.get('equipment', '?')
                    print(f"    - {name} ({equip})")
    
    # Save
    with open('test_plan_older_beginner.json', 'w') as f:
        json.dump(plan, f, indent=2)
    
    print("\n💾 Saved to: test_plan_older_beginner.json")
    print("\n✅ Check if exercises are appropriate for 65-year-old beginner!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
