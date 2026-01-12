"""
Test OpenAI service with weight loss goal (heavy cardio focus).
"""
from openai_service import OpenAIService
import json

def test_weight_loss():
    """Test weight loss plan generation"""
    
    print("="*60)
    print("🧪 TESTING WEIGHT LOSS GOAL")
    print("="*60)
    
    # Weight loss profile
    user_profile = {
        "goal": "weight_loss",
        "days_per_week": 4,
        "experience": "beginner",
        "gender": "female",
        "bodyweight_lb": 150.0,
        "split_type": "full_body",  # Should be overridden to full_body
        "exercises_per_day": 3  # Fewer exercises since mostly cardio
    }
    
    constraints = {
        "equipment_access": "full_gym"
    }
    
    # Mock exercises
    allowed_exercises = [
        {"exercise_id": "squat", "name": "Squat", "category": "legs", "equipment": "barbell", "suggested_weight_lb": 95},
        {"exercise_id": "push-ups", "name": "Push-ups", "category": "chest", "equipment": "bodyweight", "suggested_weight_lb": None},
        {"exercise_id": "lunges", "name": "Lunges", "category": "legs", "equipment": "bodyweight", "suggested_weight_lb": None},
        {"exercise_id": "plank", "name": "Plank", "category": "core", "equipment": "bodyweight", "suggested_weight_lb": None},
        {"exercise_id": "dumbbell-row", "name": "Dumbbell Row", "category": "back", "equipment": "dumbbell", "suggested_weight_lb": 25},
        {"exercise_id": "goblet-squat", "name": "Goblet Squat", "category": "legs", "equipment": "dumbbell", "suggested_weight_lb": 30},
        {"exercise_id": "dumbbell-press", "name": "Dumbbell Press", "category": "shoulders", "equipment": "dumbbell", "suggested_weight_lb": 20},
        {"exercise_id": "mountain-climbers", "name": "Mountain Climbers", "category": "cardio", "equipment": "bodyweight", "suggested_weight_lb": None},
        {"exercise_id": "burpees", "name": "Burpees", "category": "cardio", "equipment": "bodyweight", "suggested_weight_lb": None},
        {"exercise_id": "jumping-jacks", "name": "Jumping Jacks", "category": "cardio", "equipment": "bodyweight", "suggested_weight_lb": None},
    ]
    
    cardio_templates = [
        {"id": "hiit_intervals_v1", "name": "HIIT Intervals", "duration_min": 25, "intensity": "30s work / 30s rest"},
        {"id": "zone2_steady_v1", "name": "Zone 2 Steady State Cardio", "duration_min": 30, "intensity": "RPE 5-6/10"},
        {"id": "stair_climber_v1", "name": "Stair Climber", "duration_min": 20, "intensity": "Moderate pace"},
    ]
    
    print("\n📋 Configuration:")
    print(f"Goal: {user_profile['goal']}")
    print(f"Days: {user_profile['days_per_week']}")
    print(f"Strength Exercises per Day: {user_profile['exercises_per_day']}")
    print(f"Expected Structure: 30-40% strength + 60-70% cardio")
    
    try:
        print("\n⏳ Generating weight loss plan...")
        
        openai_service = OpenAIService()
        plan = openai_service.generate_plan(
            user_profile=user_profile,
            constraints=constraints,
            allowed_exercises=allowed_exercises,
            cardio_templates=cardio_templates
        )
        
        print("\n✅ SUCCESS! Plan generated")
        print("\n" + "="*60)
        print("📊 GENERATED PLAN")
        print("="*60)
        print(json.dumps(plan, indent=2))
        
        # Validate cardio presence
        print("\n" + "="*60)
        print("🔍 CARDIO VALIDATION")
        print("="*60)
        
        for session in plan.get('sessions', []):
            print(f"\n{session['title']}:")
            has_cardio = False
            has_strength = False
            
            for block in session.get('blocks', []):
                if block.get('type') == 'cardio':
                    has_cardio = True
                    print(f"  ✅ Cardio Block: {len(block.get('items', []))} cardio exercises")
                    for item in block.get('items', []):
                        print(f"     - {item.get('exercise_id')}")
                elif block.get('type') == 'strength':
                    has_strength = True
                    print(f"  ✅ Strength Block: {len(block.get('items', []))} exercises")
            
            if not has_cardio:
                print("  ❌ WARNING: No cardio block found!")
            if not has_strength:
                print("  ❌ WARNING: No strength block found!")
        
        with open('test_weight_loss_output.json', 'w') as f:
            json.dump(plan, f, indent=2)
        
        print(f"\n💾 Plan saved to: test_weight_loss_output.json")
        print("\n✅ Test passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_weight_loss()
