#!/usr/bin/env python3
"""
Interactive CLI test for AI plan generation.
Prompts you for each input and calls the API.
"""
import requests
import json
import sys


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_section(text):
    """Print a section header"""
    print(f"\n{text}")
    print("-" * 40)


def get_input(prompt, options=None, default=None):
    """Get user input with optional validation"""
    if options:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        if default:
            print(f"  (Press Enter for default: {default})")
        
        while True:
            choice = input("\nYour choice: ").strip()
            if not choice and default:
                return default
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                print(f"❌ Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("❌ Please enter a valid number")
    else:
        if default:
            value = input(f"{prompt} [{default}]: ").strip()
            return value if value else default
        return input(f"{prompt}: ").strip()


def main():
    """Run interactive test"""
    print_header("🏋️  AI WORKOUT PLAN GENERATOR - Interactive Test")
    print("\nThis will guide you through generating a personalized workout plan.")
    print("You'll answer a few questions, then we'll call the API.")
    
    # Get API URL
    print_section("API Configuration")
    api_url = get_input(
        "Enter API URL",
        default="http://localhost:8000"
    )
    
    # Get user ID
    user_id = get_input(
        "Enter user ID (or press Enter for 'test_user')",
        default="test_user"
    )
    
    # User Profile Questions
    print_section("👤 User Profile")
    
    # Goal
    goal_options = ["strength", "hypertrophy", "weight_loss", "general_fitness"]
    goal_display = ["Strength Gain", "Hypertrophy (Muscle Building)", "Weight Loss", "General Fitness"]
    goal = get_input("What's your primary fitness goal?", goal_display)
    goal_value = goal_options[goal_display.index(goal)]
    
    # Days per week
    days_options = ["3", "4", "5", "6"]
    days = get_input("How many days per week can you train?", days_options, default="4")
    days_per_week = int(days)
    
    # Experience level
    experience_options = ["beginner", "intermediate", "advanced"]
    experience_display = ["Beginner (< 1 year)", "Intermediate (1-3 years)", "Advanced (3+ years)"]
    experience = get_input("What's your experience level?", experience_display)
    experience_value = experience_options[experience_display.index(experience)]
    
    # Gender
    gender_options = ["male", "female"]
    gender_display = ["Male", "Female"]
    gender = get_input("What's your gender?", gender_display)
    gender_value = gender_options[gender_display.index(gender)]
    
    # Age
    age = get_input("What's your age?", default="30")
    age_years = int(age)
    
    # Bodyweight
    bodyweight = get_input("What's your bodyweight (in pounds)?", default="150")
    bodyweight_lb = float(bodyweight)
    
    # Constraints
    print_section("⚙️  Workout Preferences")
    
    # Split type (only for strength/hypertrophy)
    split_value = None
    if goal_value in ["strength", "hypertrophy"]:
        split_options = ["upper_lower", "push_pull_legs", "full_body", "bro_split"]
        split_display = [
            "Upper/Lower",
            "Push/Pull/Legs",
            "Full Body",
            "Bro Split (Chest/Back/Shoulders/Legs/Arms)"
        ]
        split = get_input("What split type do you prefer?", split_display)
        split_value = split_options[split_display.index(split)]
    else:
        # For weight_loss and general_fitness, use full_body split
        split_value = "full_body"
    
    # Exercises per day
    exercises_options = ["4", "5", "6", "7", "8"]
    exercises_display = [
        "4 exercises (Quick workout)",
        "5 exercises (Standard)",
        "6 exercises (Comprehensive)",
        "7 exercises (Extended)",
        "8 exercises (Maximum volume)"
    ]
    exercises = get_input("How many exercises per workout?", exercises_display, default="6 exercises (Comprehensive)")
    exercises_per_day = int(exercises_options[exercises_display.index(exercises)])
    
    # Equipment
    equipment_options = ["full_gym", "dumbbells_only", "home_gym", "bodyweight_only"]
    equipment_display = [
        "Full Gym (barbell, dumbbell, machines, cables)",
        "Dumbbells Only (dumbbell + bodyweight)",
        "Home Gym (dumbbells + bands + bodyweight)",
        "Bodyweight Only"
    ]
    equipment = get_input("What equipment do you have access to?", equipment_display, default="Full Gym (barbell, dumbbell, machines, cables)")
    equipment_value = equipment_options[equipment_display.index(equipment)]
    
    # Build request payload
    payload = {
        "user_id": user_id,
        "user_profile": {
            "goal": goal_value,
            "days_per_week": days_per_week,
            "experience": experience_value,
            "gender": gender_value,
            "age": age_years,
            "bodyweight_lb": bodyweight_lb,
            "split_type": split_value,
            "exercises_per_day": exercises_per_day
        },
        "constraints": {
            "equipment_access": equipment_value
        }
    }
    
    # Show summary
    print_section("📋 Your Profile Summary")
    print(f"Goal: {goal} ({goal_value})")
    if goal_value in ["strength", "hypertrophy"]:
        split_display_text = split_display[split_options.index(split_value)]
        print(f"Split Type: {split_display_text} ({split_value})")
    else:
        print(f"Split Type: Full Body (default for {goal_value})")
    print(f"Days/Week: {days_per_week}")
    print(f"Exercises per Day: {exercises_per_day}")
    print(f"Experience: {experience} ({experience_value})")
    print(f"Gender: {gender} ({gender_value})")
    print(f"Age: {age_years} years")
    print(f"Bodyweight: {bodyweight_lb} lb")
    print(f"Equipment: {equipment} ({equipment_value})")
    
    # Confirm
    confirm = input("\n✅ Generate plan with these settings? (y/n) [y]: ").strip().lower()
    if confirm and confirm != 'y':
        print("\n❌ Cancelled. Exiting...")
        sys.exit(0)
    
    # Make API request
    print_section("🚀 Calling API...")
    endpoint = f"{api_url}/plans/generate"
    print(f"Endpoint: {endpoint}")
    print("\n⏳ Generating your personalized workout plan...")
    print("   (This may take 10-30 seconds with OpenAI)")
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        # Print response
        print_section("📡 API Response")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("\n✅ SUCCESS! Plan generated successfully!\n")
                
                plan = data.get('plan', {})
                overview = plan.get('overview', {})
                sessions = plan.get('sessions', [])
                metadata = data.get('metadata', {})
                
                # Show overview
                print_header("📊 PLAN OVERVIEW")
                print(f"Goal: {overview.get('goal', 'N/A')}")
                print(f"Days per Week: {overview.get('days_per_week', 'N/A')}")
                print(f"Session Length: {overview.get('session_length_minutes', 'N/A')} minutes")
                print(f"Notes: {overview.get('notes', 'N/A')}")
                
                # Show metadata
                print(f"\nGeneration Method: {metadata.get('generation_method', 'N/A')}")
                print(f"Model: {metadata.get('model', 'N/A')}")
                print(f"Exercises Considered: {metadata.get('exercises_considered', 'N/A')}")
                
                # Show sessions
                print_header("🗓️  WORKOUT SESSIONS")
                for i, session in enumerate(sessions, 1):
                    print(f"\n{'='*60}")
                    print(f"Session {i}: {session.get('title', 'Untitled')}")
                    print(f"{'='*60}")
                    
                    for block in session.get('blocks', []):
                        block_type = block.get('type', 'unknown')
                        print(f"\n{block_type.upper()} BLOCK:")
                        print("-" * 40)
                        
                        for item in block.get('items', []):
                            exercise_name = item.get('exercise_name', item.get('exercise_id', 'Unknown'))
                            sets = item.get('sets', 'N/A')
                            reps = item.get('reps', 'N/A')
                            rest = item.get('rest_seconds', 'N/A')
                            notes = item.get('notes', '')
                            
                            print(f"\n• {exercise_name}")
                            print(f"  Sets: {sets} | Reps: {reps} | Rest: {rest}s")
                            if notes:
                                print(f"  Notes: {notes}")
                
                # Ask to save
                print("\n" + "="*60)
                save = input("\n💾 Save full plan to JSON file? (y/n) [n]: ").strip().lower()
                if save == 'y':
                    filename = f"workout_plan_{user_id}_{goal_value}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"\n✅ Plan saved to: {filename}")
                
            else:
                print("\n❌ FAILED: Plan generation unsuccessful")
                print(f"Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"\n❌ REQUEST FAILED with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"\nError Details:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"\nResponse: {response.text}")
    
    except requests.exceptions.Timeout:
        print("\n❌ REQUEST TIMEOUT")
        print("The API took too long to respond (>60s)")
        print("This might happen if OpenAI is slow. Try again.")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR")
        print(f"Could not connect to {api_url}")
        print("Make sure your API server is running!")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user. Exiting...\n")
        sys.exit(0)
