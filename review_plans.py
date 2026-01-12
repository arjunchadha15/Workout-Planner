"""
Quick review helper - Display key metrics from generated plans
"""
import json
import os
import glob


def review_plan_file(filename):
    """Display key metrics from a plan file"""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    test_name = data['test_name']
    profile = data['user_profile']
    plan = data['plan']
    constraint = data.get('constraint')
    
    print(f"\n{'='*80}")
    print(f"📄 {test_name}")
    print(f"{'='*80}")
    
    # User profile
    print(f"👤 Profile: {profile['age']}yo {profile['gender']}, {profile['experience']}, {profile['body_weight_lb']} lb")
    print(f"🎯 Goal: {profile['goal']}")
    print(f"📅 {profile['days_per_week']} days/week, {profile['exercises_per_day']} exercises/day")
    print(f"🏋️  Equipment: {profile['equipment_access']}")
    print(f"📊 Split: {profile['split_type']}")
    if constraint:
        print(f"⚙️  Constraint: \"{constraint}\"")
    
    # Plan overview
    overview = plan['overview']
    sessions = plan['sessions']
    
    print(f"\n📋 Generated Plan:")
    print(f"   Days: {overview['days_per_week']} | Split: {overview['split_type']} | Exercises/day: {overview['exercises_per_day']}")
    
    # Quality checks
    issues = []
    
    # Check each session
    total_strength = 0
    total_cardio = 0
    sessions_with_cardio = 0
    
    for i, session in enumerate(sessions, 1):
        strength_count = 0
        cardio_count = 0
        exercises = []
        
        for block in session['blocks']:
            if block['type'] == 'strength':
                strength_count += len(block['items'])
                total_strength += len(block['items'])
                for item in block['items']:
                    exercises.append(item['exercise_id'])
            elif block['type'] == 'cardio':
                cardio_count += 1
                total_cardio += 1
                sessions_with_cardio += 1
        
        # Check for duplicates
        duplicates = [ex for ex in exercises if exercises.count(ex) > 1]
        if duplicates:
            issues.append(f"Day {i}: Duplicate exercises - {set(duplicates)}")
        
        # Check exercise count
        if strength_count != overview['exercises_per_day']:
            issues.append(f"Day {i}: Expected {overview['exercises_per_day']} exercises, got {strength_count}")
    
    # Cardio percentage check
    cardio_percentage = (sessions_with_cardio / len(sessions)) * 100
    expected_cardio = {
        'weight_loss': 70,
        'general_fitness': 50,
        'strength': 0,
        'hypertrophy': 0
    }
    
    expected = expected_cardio.get(profile['goal'], 0)
    if abs(cardio_percentage - expected) > 20:  # Allow 20% tolerance
        issues.append(f"Cardio percentage: {cardio_percentage:.0f}% (expected ~{expected}%)")
    
    print(f"\n📊 Metrics:")
    print(f"   Total strength exercises: {total_strength}")
    print(f"   Total cardio blocks: {total_cardio}")
    print(f"   Sessions with cardio: {sessions_with_cardio}/{len(sessions)} ({cardio_percentage:.0f}%)")
    
    # Show sample exercises from first session
    print(f"\n🏋️  Day 1 exercises:")
    first_session = sessions[0]
    for block in first_session['blocks']:
        if block['type'] == 'strength':
            for item in block['items'][:5]:
                weight = item.get('suggested_weight_lb', 'BW')
                print(f"      - {item['exercise_id']}: {item['sets']}x{item['reps']} @ {weight} lb")
        elif block['type'] == 'cardio':
            print(f"      - Cardio: {block.get('cardio_id', 'N/A')} @ {block.get('zone', 'N/A')} for {block.get('duration_minutes', 'N/A')} min")
    
    # Quality assessment
    if issues:
        print(f"\n⚠️  Issues found:")
        for issue in issues:
            print(f"      - {issue}")
    else:
        print(f"\n✅ No issues detected!")
    
    return len(issues) == 0


def main():
    """Review all generated plan files"""
    print("\n" + "="*80)
    print("📝 PLAN REVIEW HELPER")
    print("="*80)
    
    # Find all review files
    review_files = sorted(glob.glob('review_*.json'))
    
    if not review_files:
        print("❌ No review files found. Run test_comprehensive_suite.py first.")
        return
    
    print(f"\nFound {len(review_files)} plan files to review\n")
    
    all_passed = True
    for filename in review_files:
        passed = review_plan_file(filename)
        if not passed:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL PLANS PASSED QUALITY CHECKS")
    else:
        print("⚠️  SOME PLANS HAVE ISSUES - REVIEW ABOVE")
    print("="*80 + "\n")
    
    print("💡 To review full plan details, open the JSON files:")
    for filename in review_files:
        print(f"   {filename}")
    print()


if __name__ == "__main__":
    main()
