"""
Test constraint parsing with natural language inputs
"""
from constraint_parser import ConstraintParser

parser = ConstraintParser()

print("="*60)
print("🧪 TESTING CONSTRAINT PARSER")
print("="*60)

# Test cases
test_cases = [
    {
        'input': "I only have dumbbells and a pull-up bar",
        'profile': {'goal': 'hypertrophy', 'age': 25, 'experience': 'intermediate', 'days_per_week': 4}
    },
    {
        'input': "I want to do PPL with abs at the end of every workout",
        'profile': {'goal': 'hypertrophy', 'age': 22, 'experience': 'intermediate', 'days_per_week': 6}
    },
    {
        'input': "Arnold split with cardio after each session",
        'profile': {'goal': 'strength', 'age': 28, 'experience': 'advanced', 'days_per_week': 6}
    },
    {
        'input': "Just bodyweight exercises at home",
        'profile': {'goal': 'general_fitness', 'age': 45, 'experience': 'beginner', 'days_per_week': 3}
    },
    {
        'input': "I have barbell, dumbbells, and a treadmill",
        'profile': {'goal': 'weight_loss', 'age': 35, 'experience': 'beginner', 'days_per_week': 4}
    },
    {
        'input': "",  # Empty - should default to full gym
        'profile': {'goal': 'strength', 'age': 30, 'experience': 'intermediate', 'days_per_week': 4}
    },
    {
        'input': "Arnold split",  # Invalid - only 3 days
        'profile': {'goal': 'hypertrophy', 'age': 25, 'experience': 'intermediate', 'days_per_week': 3}
    },
    {
        'input': "PPL split",  # Invalid - weight loss must use full body
        'profile': {'goal': 'weight_loss', 'age': 30, 'experience': 'beginner', 'days_per_week': 5}
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*60}")
    print(f"Test {i}")
    print(f"{'='*60}")
    print(f"Input: \"{test['input']}\"")
    print(f"Profile: {test['profile']['age']} yrs, {test['profile']['experience']}, {test['profile']['goal']}")
    
    result = parser.parse_constraints(test['input'], test['profile'])
    
    print(f"\n✅ Parsed Constraints:")
    print(f"  Equipment: {result['equipment_access']}")
    if result['specific_equipment']:
        print(f"  Specific: {result['specific_equipment']}")
    if result['custom_split']:
        print(f"  Split: {result['custom_split']}")
    print(f"  Add Abs: {result['add_abs']}")
    print(f"  Add Cardio: {result['add_cardio']}")
    
    if result['modifications']:
        print(f"\n📝 Modifications:")
        for mod in result['modifications']:
            print(f"  - {mod}")
    
    if result['warnings']:
        print(f"\n⚠️  Warnings:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    # Show OpenAI prompt addition
    prompt_addition = parser.format_constraints_for_openai(result)
    if prompt_addition:
        print(f"\n📋 OpenAI Prompt Addition:")
        print(prompt_addition[:200] + "..." if len(prompt_addition) > 200 else prompt_addition)

print("\n" + "="*60)
print("✅ CONSTRAINT PARSING TESTS COMPLETE")
print("="*60)
