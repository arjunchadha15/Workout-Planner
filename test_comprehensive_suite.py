"""
Comprehensive test suite for all goals and demographics.
Generates plans for review and quality assurance.

Tests cover:
- All 4 goals (strength, hypertrophy, weight_loss, general_fitness)
- Different demographics (age, gender, experience)
- Equipment variations
- Constraint scenarios
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from ai_plan_generation_service import AIPlanGenerationService
import json
import os
from datetime import datetime


def setup_database():
    """Setup real database connection"""
    engine = create_engine(Config.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def save_plan_for_review(plan, test_name, user_profile, constraint_text=None):
    """Save plan to JSON file with metadata for review"""
    output = {
        "test_name": test_name,
        "generated_at": datetime.now().isoformat(),
        "user_profile": user_profile,
        "constraint": constraint_text,
        "plan": plan
    }
    
    filename = f"review_{test_name}.json"
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    return filename


def analyze_plan(plan, test_name):
    """Analyze plan and print quality metrics"""
    overview = plan['overview']
    sessions = plan['sessions']
    
    print(f"\n{'='*80}")
    print(f"📊 ANALYSIS: {test_name}")
    print(f"{'='*80}")
    print(f"Goal: {overview['goal']}")
    print(f"Days per week: {overview['days_per_week']}")
    print(f"Split: {overview['split_type']}")
    print(f"Exercises per day: {overview['exercises_per_day']}")
    print(f"Total sessions: {len(sessions)}")
    
    # Check each session
    for i, session in enumerate(sessions, 1):
        strength_count = 0
        cardio_count = 0
        exercises = []
        
        for block in session['blocks']:
            if block['type'] == 'strength':
                strength_count += len(block['items'])
                for item in block['items']:
                    exercises.append(item['exercise_id'])
            elif block['type'] == 'cardio':
                cardio_count += 1
        
        # Check for duplicates
        duplicates = len(exercises) - len(set(exercises))
        
        print(f"\n  Day {i}:")
        print(f"    Strength exercises: {strength_count}")
        print(f"    Cardio blocks: {cardio_count}")
        if duplicates > 0:
            print(f"    ⚠️  DUPLICATE EXERCISES: {duplicates}")
        print(f"    Exercises: {', '.join(exercises[:3])}..." if len(exercises) > 3 else f"    Exercises: {', '.join(exercises)}")
    
    print(f"\n{'='*80}\n")


def test_strength_young_male():
    """Test 1: Strength - Young Male, Advanced"""
    print("\n🏋️ TEST 1: Strength Goal - Young Male Advanced")
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 24,
        'gender': 'male',
        'body_weight_lb': 185,
        'goal': 'strength',
        'experience': 'advanced',
        'days_per_week': 4,
        'exercises_per_day': 5,
        'equipment_access': 'full_gym',
        'split_type': 'upper_lower'
    }
    
    result = service.generate_plan(user_id='test_strength_young', user_profile=user_profile)
    plan = result['plan']
    
    filename = save_plan_for_review(plan, 'strength_young_male_advanced', user_profile)
    analyze_plan(plan, 'Strength - Young Male Advanced')
    
    db.close()
    return filename


def test_strength_older_beginner():
    """Test 2: Strength - Older Male Beginner"""
    print("\n🏋️ TEST 2: Strength Goal - Older Male Beginner")
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 58,
        'gender': 'male',
        'body_weight_lb': 195,
        'goal': 'strength',
        'experience': 'beginner',
        'days_per_week': 3,
        'exercises_per_day': 5,
        'equipment_access': 'full_gym',
        'split_type': 'full_body'
    }
    
    result = service.generate_plan(user_id='test_strength_older', user_profile=user_profile)
    plan = result['plan']
    
    filename = save_plan_for_review(plan, 'strength_older_male_beginner', user_profile)
    analyze_plan(plan, 'Strength - Older Male Beginner')
    
    db.close()
    return filename


def test_hypertrophy_female_intermediate():
    """Test 3: Hypertrophy - Female Intermediate"""
    print("\n💪 TEST 3: Hypertrophy Goal - Female Intermediate")
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 28,
        'gender': 'female',
        'body_weight_lb': 135,
        'goal': 'hypertrophy',
        'experience': 'intermediate',
        'days_per_week': 5,
        'exercises_per_day': 6,
        'equipment_access': 'full_gym',
        'split_type': 'push_pull_legs'
    }
    
    result = service.generate_plan(user_id='test_hypertrophy_female', user_profile=user_profile)
    plan = result['plan']
    
    filename = save_plan_for_review(plan, 'hypertrophy_female_intermediate', user_profile)
    analyze_plan(plan, 'Hypertrophy - Female Intermediate')
    
    db.close()
    return filename


def test_hypertrophy_male_ppl_with_abs():
    """Test 4: Hypertrophy - Male PPL with abs constraint"""
    print("\n💪 TEST 4: Hypertrophy Goal - Male PPL with Abs on Leg Days")
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 26,
        'gender': 'male',
        'body_weight_lb': 175,
        'goal': 'hypertrophy',
        'experience': 'intermediate',
        'days_per_week': 6,
        'exercises_per_day': 5,
        'equipment_access': 'full_gym',
        'split_type': 'push_pull_legs'
    }
    
    constraint = 'add abs at the end of leg days'
    
    result = service.generate_plan(
        user_id='test_hypertrophy_abs',
        user_profile=user_profile,
        constraint_text=constraint
    )
    plan = result['plan']
    
    filename = save_plan_for_review(plan, 'hypertrophy_male_ppl_abs', user_profile, constraint)
    analyze_plan(plan, 'Hypertrophy - Male PPL with Abs')
    
    # Check abs placement
    abs_keywords = ['crunch', 'plank', 'sit-up', 'leg-raise', 'woodchopper', 'bicycle', 'russian-twist']
    print("  Abs placement check (should be on Day 3 and Day 6):")
    for i, session in enumerate(plan['sessions'], 1):
        has_abs = False
        for block in session['blocks']:
            if block['type'] == 'strength':
                for item in block['items']:
                    if any(kw in item['exercise_id'].lower() for kw in abs_keywords):
                        has_abs = True
        day_type = "(LEG)" if i in [3, 6] else ""
        print(f"    Day {i} {day_type}: {'✅ Has abs' if has_abs else '❌ No abs'}")
    
    db.close()
    return filename


def test_weight_loss_female_beginner():
    """Test 5: Weight Loss - Female Beginner"""
    print("\n🏃 TEST 5: Weight Loss Goal - Female Beginner")
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 35,
        'gender': 'female',
        'body_weight_lb': 160,
        'goal': 'weight_loss',
        'experience': 'beginner',
        'days_per_week': 4,
        'exercises_per_day': 5,
        'equipment_access': 'full_gym',
        'split_type': 'full_body'
    }
    
    result = service.generate_plan(user_id='test_weight_loss_female', user_profile=user_profile)
    plan = result['plan']
    
    filename = save_plan_for_review(plan, 'weight_loss_female_beginner', user_profile)
    analyze_plan(plan, 'Weight Loss - Female Beginner')
    
    # Check cardio presence (should be 70% of sessions for weight loss)
    cardio_sessions = 0
    for session in plan['sessions']:
        for block in session['blocks']:
            if block['type'] == 'cardio':
                cardio_sessions += 1
                break
    
    print(f"  Cardio check: {cardio_sessions}/{len(plan['sessions'])} sessions have cardio")
    print(f"  Expected: ~70% = {int(len(plan['sessions']) * 0.7)} sessions")
    
    db.close()
    return filename


def test_weight_loss_male_advanced():
    """Test 6: Weight Loss - Male Advanced"""
    print("\n🏃 TEST 6: Weight Loss Goal - Male Advanced")
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 42,
        'gender': 'male',
        'body_weight_lb': 210,
        'goal': 'weight_loss',
        'experience': 'advanced',
        'days_per_week': 5,
        'exercises_per_day': 6,
        'equipment_access': 'full_gym',
        'split_type': 'full_body'
    }
    
    result = service.generate_plan(user_id='test_weight_loss_male', user_profile=user_profile)
    plan = result['plan']
    
    filename = save_plan_for_review(plan, 'weight_loss_male_advanced', user_profile)
    analyze_plan(plan, 'Weight Loss - Male Advanced')
    
    # Check cardio zones
    print("  Cardio zones (advanced users should see zone3/zone4):")
    for i, session in enumerate(plan['sessions'], 1):
        for block in session['blocks']:
            if block['type'] == 'cardio':
                print(f"    Day {i}: {block.get('zone', 'N/A')} for {block.get('duration_minutes', 'N/A')} min")
    
    db.close()
    return filename


def test_general_fitness_young_female():
    """Test 7: General Fitness - Young Female"""
    print("\n🎯 TEST 7: General Fitness Goal - Young Female Beginner")
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 22,
        'gender': 'female',
        'body_weight_lb': 125,
        'goal': 'general_fitness',
        'experience': 'beginner',
        'days_per_week': 3,
        'exercises_per_day': 5,
        'equipment_access': 'full_gym',
        'split_type': 'full_body'
    }
    
    result = service.generate_plan(user_id='test_general_young', user_profile=user_profile)
    plan = result['plan']
    
    filename = save_plan_for_review(plan, 'general_fitness_young_female', user_profile)
    analyze_plan(plan, 'General Fitness - Young Female')
    
    # Check cardio presence (should be ~50% for general fitness)
    cardio_sessions = 0
    for session in plan['sessions']:
        for block in session['blocks']:
            if block['type'] == 'cardio':
                cardio_sessions += 1
                break
    
    print(f"  Cardio check: {cardio_sessions}/{len(plan['sessions'])} sessions have cardio")
    print(f"  Expected: ~50% = {int(len(plan['sessions']) * 0.5)} sessions")
    
    db.close()
    return filename


def test_general_fitness_older_male():
    """Test 8: General Fitness - Older Male"""
    print("\n🎯 TEST 8: General Fitness Goal - Older Male Intermediate")
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 62,
        'gender': 'male',
        'body_weight_lb': 180,
        'goal': 'general_fitness',
        'experience': 'intermediate',
        'days_per_week': 4,
        'exercises_per_day': 5,
        'equipment_access': 'full_gym',
        'split_type': 'full_body'
    }
    
    result = service.generate_plan(user_id='test_general_older', user_profile=user_profile)
    plan = result['plan']
    
    filename = save_plan_for_review(plan, 'general_fitness_older_male', user_profile)
    analyze_plan(plan, 'General Fitness - Older Male')
    
    # Check for safe exercises
    print("  First session exercises (should be joint-friendly for older user):")
    first_session = plan['sessions'][0]
    for block in first_session['blocks']:
        if block['type'] == 'strength':
            for item in block['items'][:5]:
                print(f"    - {item['exercise_id']}: {item['sets']}x{item['reps']}")
    
    db.close()
    return filename


def test_dumbbells_only_home_gym():
    """Test 9: Home Gym - Dumbbells Only"""
    print("\n🏠 TEST 9: Equipment Constraint - Dumbbells Only")
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 30,
        'gender': 'male',
        'body_weight_lb': 170,
        'goal': 'hypertrophy',
        'experience': 'intermediate',
        'days_per_week': 4,
        'exercises_per_day': 6,
        'equipment_access': 'full_gym',  # Will be overridden
        'split_type': 'upper_lower'
    }
    
    constraint = 'i only have dumbbells and a pull-up bar'
    
    result = service.generate_plan(
        user_id='test_dumbbells',
        user_profile=user_profile,
        constraint_text=constraint
    )
    plan = result['plan']
    
    filename = save_plan_for_review(plan, 'equipment_dumbbells_only', user_profile, constraint)
    analyze_plan(plan, 'Equipment - Dumbbells Only')
    
    # Sample exercises
    print("  Sample exercises (should use dumbbells/bodyweight only):")
    for block in plan['sessions'][0]['blocks']:
        if block['type'] == 'strength':
            for item in block['items'][:3]:
                print(f"    - {item['exercise_id']}")
    
    db.close()
    return filename


def test_every_workout_abs_cardio():
    """Test 10: Constraint - Abs and Cardio Every Workout"""
    print("\n🎯 TEST 10: Constraint - Abs and Cardio Every Workout")
    
    db = setup_database()
    service = AIPlanGenerationService(db)
    
    user_profile = {
        'age': 28,
        'gender': 'female',
        'body_weight_lb': 140,
        'goal': 'general_fitness',
        'experience': 'intermediate',
        'days_per_week': 4,
        'exercises_per_day': 5,
        'equipment_access': 'full_gym',
        'split_type': 'full_body'
    }
    
    constraint = 'add abs and cardio at the end of every workout'
    
    result = service.generate_plan(
        user_id='test_abs_cardio_all',
        user_profile=user_profile,
        constraint_text=constraint
    )
    plan = result['plan']
    
    filename = save_plan_for_review(plan, 'constraint_abs_cardio_every_workout', user_profile, constraint)
    analyze_plan(plan, 'Constraint - Abs and Cardio Every Workout')
    
    # Check each session
    abs_keywords = ['crunch', 'plank', 'sit-up', 'leg-raise', 'woodchopper', 'bicycle', 'russian-twist']
    print("  Checking abs and cardio presence (should be in ALL sessions):")
    for i, session in enumerate(plan['sessions'], 1):
        has_abs = False
        has_cardio = False
        
        for block in session['blocks']:
            if block['type'] == 'strength':
                for item in block['items']:
                    if any(kw in item['exercise_id'].lower() for kw in abs_keywords):
                        has_abs = True
            elif block['type'] == 'cardio':
                has_cardio = True
        
        status_abs = "✅" if has_abs else "❌"
        status_cardio = "✅" if has_cardio else "❌"
        print(f"    Day {i}: Abs {status_abs} | Cardio {status_cardio}")
    
    db.close()
    return filename


def generate_summary_report(test_results):
    """Generate a summary report of all tests"""
    report = {
        "test_suite": "Comprehensive Goal and Demographic Testing",
        "generated_at": datetime.now().isoformat(),
        "total_tests": len(test_results),
        "test_files": test_results,
        "goals_tested": [
            "strength (young advanced, older beginner)",
            "hypertrophy (female intermediate, male with constraints)",
            "weight_loss (female beginner, male advanced)",
            "general_fitness (young female, older male)"
        ],
        "demographics_tested": [
            "Age: 22-62 years",
            "Gender: Male and Female",
            "Experience: Beginner, Intermediate, Advanced",
            "Body weight: 125-210 lbs"
        ],
        "constraints_tested": [
            "Abs on specific days (leg days)",
            "Equipment limitations (dumbbells only)",
            "Abs and cardio every workout"
        ],
        "review_instructions": [
            "1. Check for duplicate exercises within same session",
            "2. Verify cardio percentage matches goal (weight_loss: 70%, general: 50%)",
            "3. Confirm split types match days per week",
            "4. Validate exercise difficulty matches experience level",
            "5. Ensure older users get joint-friendly exercises",
            "6. Check constraint compliance (abs placement, equipment usage)"
        ]
    }
    
    with open('review_summary.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*80)
    print("📋 TEST SUITE SUMMARY")
    print("="*80)
    print(f"Total tests run: {len(test_results)}")
    print(f"\nGenerated files for review:")
    for filename in test_results:
        print(f"  - {filename}")
    print(f"\nSummary report: review_summary.json")
    print("\n✅ All plans generated successfully!")
    print("Please review the JSON files to ensure quality.")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE TEST SUITE - ALL GOALS & DEMOGRAPHICS")
    print("="*80)
    print("Generating plans for all combinations...")
    print("Using REAL database (Supabase PostgreSQL)")
    print("="*80)
    
    test_results = []
    
    try:
        # STRENGTH TESTS
        test_results.append(test_strength_young_male())
        test_results.append(test_strength_older_beginner())
        
        # HYPERTROPHY TESTS
        test_results.append(test_hypertrophy_female_intermediate())
        test_results.append(test_hypertrophy_male_ppl_with_abs())
        
        # WEIGHT LOSS TESTS
        test_results.append(test_weight_loss_female_beginner())
        test_results.append(test_weight_loss_male_advanced())
        
        # GENERAL FITNESS TESTS
        test_results.append(test_general_fitness_young_female())
        test_results.append(test_general_fitness_older_male())
        
        # CONSTRAINT TESTS
        test_results.append(test_dumbbells_only_home_gym())
        test_results.append(test_every_workout_abs_cardio())
        
        # Generate summary
        generate_summary_report(test_results)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
