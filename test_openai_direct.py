"""
Standalone test of OpenAI service without database.
Tests just the OpenAI prompt/response cycle.
"""
from openai_service import OpenAIService
from mock_cardio_database import get_mock_cardio_db
from cardio_selector import CardioSelector
import json

def test_openai_direct():
    """Test OpenAI service directly without database"""
    
    print("="*60)
    print("🧪 TESTING OPENAI SERVICE DIRECTLY")
    print("="*60)
    
    # Mock user profile
    user_profile = {
        "goal": "hypertrophy",
        "days_per_week": 5,
        "experience": "intermediate",
        "gender": "male",
        "age": 20,
        "bodyweight_lb": 140.0,
        "split_type": "push_pull_legs",
        "exercises_per_day": 5
    }
    
    # Mock constraints
    constraints = {
        "equipment_access": "full_gym"
    }
    
    # Mock allowed exercises (simplified list)
    allowed_exercises = [
        {"exercise_id": "bench-press", "name": "Bench Press", "category": "chest", "equipment": "barbell", "suggested_weight_lb": 135},
        {"exercise_id": "squat", "name": "Squat", "category": "legs", "equipment": "barbell", "suggested_weight_lb": 185},
        {"exercise_id": "deadlift", "name": "Deadlift", "category": "back", "equipment": "barbell", "suggested_weight_lb": 225},
        {"exercise_id": "overhead-press", "name": "Overhead Press", "category": "shoulders", "equipment": "barbell", "suggested_weight_lb": 95},
        {"exercise_id": "bent-over-row", "name": "Bent Over Row", "category": "back", "equipment": "barbell", "suggested_weight_lb": 115},
        {"exercise_id": "pull-ups", "name": "Pull-ups", "category": "back", "equipment": "bodyweight", "suggested_weight_lb": None},
        {"exercise_id": "dips", "name": "Dips", "category": "chest", "equipment": "bodyweight", "suggested_weight_lb": None},
        {"exercise_id": "leg-press", "name": "Leg Press", "category": "legs", "equipment": "machine", "suggested_weight_lb": 270},
        {"exercise_id": "lat-pulldown", "name": "Lat Pulldown", "category": "back", "equipment": "cable", "suggested_weight_lb": 120},
        {"exercise_id": "cable-fly", "name": "Cable Fly", "category": "chest", "equipment": "cable", "suggested_weight_lb": 40},
    ]
    
    # Get cardio options using new cardio system
    mock_cardio_repo = get_mock_cardio_db()
    cardio_selector = CardioSelector(db=None, cardio_ref_repo=mock_cardio_repo)
    allowed_cardio = cardio_selector.select_cardio_options(
        user_profile=user_profile,
        constraints=constraints
    )
    
    print("\n📋 Test Configuration:")
    print(f"Goal: {user_profile['goal']}")
    print(f"Days: {user_profile['days_per_week']}")
    print(f"Experience: {user_profile['experience']}")
    print(f"Split Type: {user_profile['split_type']}")
    print(f"Exercises per Day: {user_profile['exercises_per_day']}")
    print(f"Equipment: {constraints['equipment_access']}")
    print(f"Exercises Available: {len(allowed_exercises)}")
    print(f"Cardio Options Available: {len(allowed_cardio)}")
    print(f"Expected: Hypertrophy focus with minimal/no cardio")
    
    try:
        print("\n⏳ Calling OpenAI API...")
        print("   (This may take 10-30 seconds)")
        
        # Initialize OpenAI service
        openai_service = OpenAIService()
        
        # Generate plan
        plan = openai_service.generate_plan(
            user_profile=user_profile,
            constraints=constraints,
            allowed_exercises=allowed_exercises,
            allowed_cardio=allowed_cardio
        )
        
        print("\n✅ SUCCESS! Plan generated")
        print("\n" + "="*60)
        print("📊 GENERATED PLAN")
        print("="*60)
        print(json.dumps(plan, indent=2))
        
        # Save to file
        filename = "test_plan_output.json"
        with open(filename, 'w') as f:
            json.dump(plan, f, indent=2)
        print(f"\n💾 Plan saved to: {filename}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_openai_direct()
    if success:
        print("\n✅ Test passed!")
    else:
        print("\n❌ Test failed!")
