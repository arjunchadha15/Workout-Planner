"""
Interactive test with custom constraints
You can type your own constraints and see the full plan generated!
"""
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from ai_plan_generation_service import AIPlanGenerationService
from constraint_parser import ConstraintParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
import json

print("="*60)
print("🏋️  AI WORKOUT PLAN GENERATOR - WITH CONSTRAINTS")
print("="*60)

# Get user profile
print("\n📋 USER PROFILE")
print("-"*60)

age = int(input("Age: ").strip() or "25")

print("\nWhat's your experience level?")
print("  1. Beginner (< 1 year)")
print("  2. Intermediate (1-3 years)")
print("  3. Advanced (3+ years)")
experience_choice = int(input("Your choice [2]: ").strip() or "2")
experience = ['beginner', 'intermediate', 'advanced'][experience_choice - 1]

print("\nWhat's your gender?")
print("  1. Male")
print("  2. Female")
gender_choice = int(input("Your choice [1]: ").strip() or "1")
gender = ['male', 'female'][gender_choice - 1]

bodyweight_input = input("\nBodyweight (lb) [150]: ").strip()
try:
    bodyweight = float(bodyweight_input) if bodyweight_input else 150.0
except ValueError:
    print(f"Invalid bodyweight, using default: 150 lb")
    bodyweight = 150.0

print("\nWhat's your primary fitness goal?")
print("  1. Strength Gain")
print("  2. Hypertrophy (Muscle Building)")
print("  3. Weight Loss")
print("  4. General Fitness")
goal_choice = int(input("Your choice [2]: ").strip() or "2")
goal = ['strength', 'hypertrophy', 'weight_loss', 'general_fitness'][goal_choice - 1]

print("\nHow many days per week can you train?")
print("  1. 3")
print("  2. 4")
print("  3. 5")
print("  4. 6")
days_choice = int(input("Your choice [2]: ").strip() or "2")
days = [3, 4, 5, 6][days_choice - 1]

print("\nHow many exercises per workout?")
print("  1. 4 exercises")
print("  2. 5 exercises")
print("  3. 6 exercises")
print("  4. 7 exercises")
print("  5. 8 exercises")
exercises_choice = int(input("Your choice [2]: ").strip() or "2")
exercises_per_day = [4, 5, 6, 7, 8][exercises_choice - 1]

# Default split based on goal
if goal in ['weight_loss', 'general_fitness']:
    split = 'full_body'
    print(f"\nSplit: Full Body (required for {goal})")
else:
    print("\nWhat split type do you prefer?")
    print("  1. Upper/Lower")
    print("  2. Push/Pull/Legs")
    print("  3. Full Body")
    print("  4. Bro Split (Chest/Back/Shoulders/Legs/Arms)")
    split_choice = int(input("Your choice [1]: ").strip() or "1")
    split = ['upper_lower', 'push_pull_legs', 'full_body', 'bro_split'][split_choice - 1]

user_profile = {
    "goal": goal,
    "days_per_week": days,
    "experience": experience,
    "gender": gender,
    "age": age,
    "bodyweight_lb": bodyweight,
    "split_type": split,
    "exercises_per_day": exercises_per_day
}

print("\n" + "="*60)
print("💬 CUSTOM CONSTRAINTS (Optional)")
print("="*60)
print("\nExamples of what you can type:")
print("  - 'I only have dumbbells and a pull-up bar'")
print("  - 'I want to do PPL with abs at the end'")
print("  - 'Arnold split with cardio after each session'")
print("  - 'Add abs to every workout'")
print("  - Just press Enter for no constraints (full gym)")
print()

constraint_input = input("Your constraints: ").strip()

# Parse constraints
parser = ConstraintParser()
parsed_constraints = parser.parse_constraints(constraint_input, user_profile)

print("\n" + "="*60)
print("✅ PARSED CONSTRAINTS")
print("="*60)
print(f"Equipment: {parsed_constraints['equipment_access']}")
if parsed_constraints['specific_equipment']:
    print(f"Specific equipment: {', '.join(parsed_constraints['specific_equipment'])}")
if parsed_constraints['custom_split']:
    print(f"Custom split: {parsed_constraints['custom_split']}")
if parsed_constraints['add_abs']:
    print("✓ Adding abs to every workout")
if parsed_constraints['add_cardio']:
    print("✓ Adding cardio to every workout")

if parsed_constraints['warnings']:
    print("\n⚠️  Warnings:")
    for warning in parsed_constraints['warnings']:
        print(f"  - {warning}")

# Format constraints for OpenAI
constraints_prompt = parser.format_constraints_for_openai(parsed_constraints)
parsed_constraints['user_constraints_prompt'] = constraints_prompt

# Confirm
print("\n" + "="*60)
confirm = input("\nGenerate plan with these settings? (y/n) [y]: ").strip().lower()
if confirm and confirm != 'y':
    print("❌ Cancelled")
    sys.exit(0)

# Connect to database
print("\n" + "="*60)
print("🔄 CONNECTING TO DATABASE...")
print("="*60)

DATABASE_URL = Config.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print("✅ Database connected")
    print("\n⏳ Generating your personalized workout plan...")
    print("   (This may take 10-30 seconds with OpenAI)")
    
    service = AIPlanGenerationService(db)
    
    result = service.generate_plan(
        user_id="test_user",
        user_profile=user_profile,
        constraints=parsed_constraints
    )
    
    plan = result['plan']
    
    print("\n" + "="*60)
    print("✅ PLAN GENERATED SUCCESSFULLY!")
    print("="*60)
    
    # Display plan
    print(f"\n📊 {plan['overview']['days_per_week']}-Day {plan['overview']['split_type']} Program")
    print(f"Goal: {plan['overview']['goal'].upper()}")
    
    for i, session in enumerate(plan.get('sessions', []), 1):
        print(f"\n{'='*60}")
        print(f"DAY {i}: {session.get('title', 'Workout')}")
        print('='*60)
        
        for block in session.get('blocks', []):
            if block.get('type') == 'strength':
                print(f"\n💪 STRENGTH EXERCISES:")
                for item in block.get('items', []):
                    name = item.get('exercise_name', item.get('exercise_id'))
                    sets = item.get('sets')
                    reps = item.get('reps')
                    weight = item.get('suggested_weight_lb')
                    weight_str = f"{weight} lb" if weight else "bodyweight"
                    print(f"  • {name}")
                    print(f"    {sets} sets × {reps} reps @ {weight_str}")
            
            elif block.get('type') == 'cardio':
                cardio_id = block.get('cardio_id', 'N/A')
                zone = block.get('zone', 'N/A')
                duration = block.get('duration_minutes', 0)
                print(f"\n🏃 CARDIO:")
                print(f"  • {cardio_id.capitalize()}")
                print(f"    {zone.upper()} intensity, {duration} minutes")
    
    # Save to file
    filename = 'my_custom_plan.json'
    with open(filename, 'w') as f:
        json.dump(plan, f, indent=2)
    
    print("\n" + "="*60)
    print(f"💾 Full plan saved to: {filename}")
    print("="*60)
    print("\n✅ Your personalized workout plan is ready!")
    
    if parsed_constraints['modifications']:
        print("\n📝 Applied customizations:")
        for mod in parsed_constraints['modifications']:
            print(f"  ✓ {mod}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
