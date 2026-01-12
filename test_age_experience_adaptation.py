"""
Test AI plan generation with different age and experience combinations
to verify OpenAI uses its knowledge base for safe, individualized plans.
"""
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from ai_plan_generation_service import AIPlanGenerationService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
import json

def test_profile(description, user_profile, constraints):
    """Test a specific user profile"""
    print("\n" + "="*60)
    print(f"🧪 TESTING: {description}")
    print("="*60)
    
    # Database connection
    DATABASE_URL = Config.DATABASE_URL
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    print(f"\n📋 Profile:")
    print(f"Age: {user_profile['age']} years")
    print(f"Experience: {user_profile['experience']}")
    print(f"Goal: {user_profile['goal']}")
    print(f"Days/Week: {user_profile['days_per_week']}")
    
    try:
        service = AIPlanGenerationService(db)
        
        print("\n⏳ Generating personalized plan...")
        print("   (OpenAI will use age/experience to select safe exercises)")
        
        result = service.generate_plan(
            user_id="test_user",
            user_profile=user_profile,
            constraints=constraints
        )
        
        plan = result['plan']
        
        print("\n✅ Plan Generated!")
        print("\n📊 Exercise Selection Analysis:")
        
        # Analyze exercises selected
        all_exercises = []
        for session in plan.get('sessions', []):
            for block in session.get('blocks', []):
                if block.get('type') == 'strength':
                    for item in block.get('items', []):
                        all_exercises.append({
                            'id': item.get('exercise_id'),
                            'name': item.get('exercise_name', item.get('exercise_id')),
                            'equipment': item.get('equipment', 'unknown')
                        })
        
        # Group by equipment type
        equipment_counts = {}
        for ex in all_exercises:
            equip = ex['equipment']
            equipment_counts[equip] = equipment_counts.get(equip, 0) + 1
        
        print("\nEquipment Distribution:")
        for equip, count in sorted(equipment_counts.items()):
            print(f"  {equip}: {count} exercises")
        
        # Show first 5 exercises
        print("\nSample Exercises Selected:")
        for ex in all_exercises[:5]:
            print(f"  - {ex['name']} ({ex['equipment']})")
        
        # Save to file
        filename = f"test_plan_{description.lower().replace(' ', '_').replace(',', '')}.json"
        with open(filename, 'w') as f:
            json.dump(plan, f, indent=2)
        
        print(f"\n💾 Full plan saved to: {filename}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def run_all_tests():
    """Run tests for different user profiles"""
    print("="*60)
    print("🏋️  AGE & EXPERIENCE ADAPTATION TEST SUITE")
    print("="*60)
    
    # Test 1: Young, Advanced (should get full exercise library)
    test_profile(
        "Young, Advanced",
        {
            "goal": "hypertrophy",
            "days_per_week": 4,
            "experience": "advanced",
            "gender": "male",
            "age": 25,
            "bodyweight_lb": 180.0,
            "split_type": "upper_lower",
            "exercises_per_day": 5
        },
        {"equipment_access": "full_gym"}
    )
    
    # Test 2: Older, Beginner (should be very conservative)
    test_profile(
        "Older, Beginner (65 years)",
        {
            "goal": "general_fitness",
            "days_per_week": 3,
            "experience": "beginner",
            "gender": "male",
            "age": 65,
            "bodyweight_lb": 160.0,
            "split_type": "full_body",
            "exercises_per_day": 4
        },
        {"equipment_access": "full_gym"}
    )
    
    # Test 3: Middle-aged, Intermediate (balanced approach)
    test_profile(
        "Middle-aged, Intermediate (45 years)",
        {
            "goal": "strength",
            "days_per_week": 4,
            "experience": "intermediate",
            "gender": "male",
            "age": 45,
            "bodyweight_lb": 175.0,
            "split_type": "upper_lower",
            "exercises_per_day": 5
        },
        {"equipment_access": "full_gym"}
    )
    
    # Test 4: Young, Beginner (basic but more variety than older beginner)
    test_profile(
        "Young, Beginner (22 years)",
        {
            "goal": "hypertrophy",
            "days_per_week": 4,
            "experience": "beginner",
            "gender": "female",
            "age": 22,
            "bodyweight_lb": 130.0,
            "split_type": "upper_lower",
            "exercises_per_day": 5
        },
        {"equipment_access": "full_gym"}
    )
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETE!")
    print("="*60)
    print("\nReview the generated plans to see how OpenAI adapted")
    print("exercise selection based on age and experience.")

if __name__ == "__main__":
    run_all_tests()
