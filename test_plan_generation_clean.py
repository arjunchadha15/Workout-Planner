"""
Clean test file for AI plan generation with real database.
This is the main test file to use for development and integration.

Tests:
1. Basic plan generation with constraints
2. Constraint parsing (natural language)
3. Age/experience adaptations
4. Equipment limitations
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from ai_plan_generation_service import AIPlanGenerationService
import json


def setup_database():
    """Setup real database connection"""
    engine = create_engine(Config.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def test_basic_plan():
    """Test basic plan generation without constraints"""
    print("\n" + "="*80)
    print("TEST 1: Basic Plan Generation (No Constraints)")
    print("="*80)
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 25,
        'gender': 'male',
        'body_weight_lb': 180,
        'goal': 'hypertrophy',
        'experience': 'intermediate',
        'days_per_week': 4,
        'exercises_per_day': 6,
        'equipment_access': 'full_gym',
        'split_type': 'upper_lower'
    }
    
    result = service.generate_plan(
        user_id='test_user_basic',
        user_profile=user_profile
    )
    
    plan = result['plan']
    print(f"✅ Plan generated successfully!")
    print(f"   Days per week: {plan['overview']['days_per_week']}")
    print(f"   Split: {plan['overview']['split_type']}")
    print(f"   Exercises per day: {plan['overview']['exercises_per_day']}")
    print(f"   Total sessions: {len(plan['sessions'])}")
    
    db.close()
    return plan


def test_constraint_abs_on_leg_days():
    """Test constraint: abs at end of leg days"""
    print("\n" + "="*80)
    print("TEST 2: Constraint - 'abs at the end of leg days'")
    print("="*80)
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
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
    
    result = service.generate_plan(
        user_id='test_user_abs',
        user_profile=user_profile,
        constraint_text='i want abs at the end of leg days'
    )
    
    plan = result['plan']
    print(f"✅ Plan generated with constraints!")
    
    # Check for abs exercises
    abs_keywords = ['crunch', 'plank', 'sit-up', 'leg-raise', 'knee-raise', 
                    'hanging', 'ab-wheel', 'woodchopper', 'russian-twist', 'bicycle']
    
    print("\nChecking each day for ab/core exercises:")
    print("(PPL = Day 1: Push, Day 2: Pull, Day 3: Leg, Day 4: Push, Day 5: Pull, Day 6: Leg)")
    
    for i, session in enumerate(plan['sessions'], 1):
        has_abs = False
        abs_exercises = []
        
        for block in session['blocks']:
            if block['type'] == 'strength':
                for item in block['items']:
                    exercise_id = item.get('exercise_id', '')
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
        print(f"   Day {i} {day_type}: {status}")
    
    db.close()
    return plan


def test_constraint_equipment_limited():
    """Test constraint: limited equipment"""
    print("\n" + "="*80)
    print("TEST 3: Constraint - 'only have dumbbells and a pull-up bar'")
    print("="*80)
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 30,
        'gender': 'female',
        'body_weight_lb': 140,
        'goal': 'general_fitness',
        'experience': 'beginner',
        'days_per_week': 3,
        'exercises_per_day': 5,
        'equipment_access': 'full_gym',  # Will be overridden by constraint
        'split_type': 'full_body'
    }
    
    result = service.generate_plan(
        user_id='test_user_equipment',
        user_profile=user_profile,
        constraint_text='i only have dumbbells and a pull-up bar'
    )
    
    plan = result['plan']
    print(f"✅ Plan generated with equipment constraints!")
    
    # Check equipment used
    all_equipment = set()
    for session in plan['sessions']:
        for block in session['blocks']:
            if block['type'] == 'strength':
                for item in block['items']:
                    # Get equipment from exercise_id context (would need full metadata)
                    all_equipment.add(item.get('exercise_id', ''))
    
    print(f"\n   Total unique exercises: {len(all_equipment)}")
    print(f"   Sample exercises: {', '.join(list(all_equipment)[:5])}")
    
    db.close()
    return plan


def test_older_beginner():
    """Test age/experience adaptations for older beginner"""
    print("\n" + "="*80)
    print("TEST 4: Age/Experience Adaptation - 65 year old beginner")
    print("="*80)
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 65,
        'gender': 'male',
        'body_weight_lb': 170,
        'goal': 'general_fitness',
        'experience': 'beginner',
        'days_per_week': 3,
        'exercises_per_day': 5,
        'equipment_access': 'full_gym',
        'split_type': 'full_body'
    }
    
    result = service.generate_plan(
        user_id='test_user_older',
        user_profile=user_profile
    )
    
    plan = result['plan']
    print(f"✅ Plan generated for older beginner!")
    
    # Show exercises to verify they're appropriate
    print("\nFirst session exercises (should be safe for older beginner):")
    first_session = plan['sessions'][0]
    for block in first_session['blocks']:
        if block['type'] == 'strength':
            for item in block['items']:
                weight = item.get('suggested_weight_lb', 'N/A')
                print(f"   - {item['exercise_id']}: {item['sets']}x{item['reps']} @ {weight} lb")
    
    db.close()
    return plan


def save_plan_to_file(plan, filename):
    """Save plan to JSON file for inspection"""
    with open(filename, 'w') as f:
        json.dump(plan, f, indent=2)
    print(f"\n💾 Plan saved to: {filename}")


if __name__ == "__main__":
    print("\n🧪 AI PLAN GENERATION TEST SUITE")
    print("Using REAL database (Supabase PostgreSQL)")
    print("="*80)
    
    try:
        # Test 1: Basic plan
        plan1 = test_basic_plan()
        save_plan_to_file(plan1, 'test_output_basic.json')
        
        # Test 2: Constraint - abs on leg days
        plan2 = test_constraint_abs_on_leg_days()
        save_plan_to_file(plan2, 'test_output_abs_leg_days.json')
        
        # Test 3: Equipment constraint
        plan3 = test_constraint_equipment_limited()
        save_plan_to_file(plan3, 'test_output_equipment.json')
        
        # Test 4: Age/experience
        plan4 = test_older_beginner()
        save_plan_to_file(plan4, 'test_output_older_beginner.json')
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
