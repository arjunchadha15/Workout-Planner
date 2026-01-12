"""
Test AI plan generation with actual database.
This test connects to your real database and uses the full service stack.
"""
import sys
import os

# Add the parent directory to path to import app modules
sys.path.insert(0, os.path.abspath('..'))

from ai_plan_generation_service import AIPlanGenerationService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
import json

def test_with_real_database():
    """Test AI plan generation with real database"""
    
    print("="*60)
    print("🧪 TESTING WITH REAL DATABASE")
    print("="*60)
    
    # Database connection from config
    DATABASE_URL = Config.DATABASE_URL
    
    print(f"\n📊 Connecting to database...")
    print(f"URL: {DATABASE_URL}")
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n⚠️  Please update DATABASE_URL in this script with your actual database URL")
        return
    
    # Test user profile - matching your interactive test
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
    
    constraints = {
        "equipment_access": "full_gym"
    }
    
    print("\n📋 Test Configuration:")
    print(f"Goal: {user_profile['goal']}")
    print(f"Split Type: {user_profile['split_type']}")
    print(f"Days: {user_profile['days_per_week']}")
    print(f"Exercises per Day: {user_profile['exercises_per_day']}")
    print(f"Experience: {user_profile['experience']}")
    print(f"Gender: {user_profile['gender']}")
    print(f"Bodyweight: {user_profile['bodyweight_lb']} lb")
    print(f"Equipment: {constraints['equipment_access']}")
    
    try:
        print("\n⏳ Initializing AI Plan Generation Service...")
        service = AIPlanGenerationService(db)
        
        print("⏳ Generating plan with OpenAI...")
        print("   (This may take 10-30 seconds)")
        
        result = service.generate_plan(
            user_id="test_user",
            user_profile=user_profile,
            constraints=constraints
        )
        
        print("\n✅ SUCCESS! Plan generated with real database")
        print("\n" + "="*60)
        print("📊 GENERATED PLAN")
        print("="*60)
        
        plan = result['plan']
        print(json.dumps(plan, indent=2))
        
        # Check if weights are present
        print("\n" + "="*60)
        print("🔍 WEIGHT VALIDATION")
        print("="*60)
        
        has_weights = False
        for session in plan.get('sessions', []):
            for block in session.get('blocks', []):
                if block.get('type') == 'strength':
                    for item in block.get('items', []):
                        if item.get('suggested_weight_lb'):
                            has_weights = True
                            print(f"✅ {item['exercise_id']}: {item['suggested_weight_lb']} lb")
        
        if not has_weights:
            print("❌ No suggested weights found in plan!")
            print("⚠️  Check that:")
            print("   1. Exercise standards exist in database")
            print("   2. OpenAI service includes weights in response")
        
        # Save to file
        with open('test_plan_real_db.json', 'w') as f:
            json.dump(plan, f, indent=2)
        
        print(f"\n💾 Plan saved to: test_plan_real_db.json")
        print("\n✅ Test passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_with_real_database()
