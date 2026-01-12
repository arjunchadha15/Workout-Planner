"""
Test script for AI plan generation.
Demonstrates how to call the plan generation endpoint.
"""
import requests
import json


# Sample request payload
SAMPLE_REQUEST_MALE_INTERMEDIATE_HYPERTROPHY = {
    "user_id": "test_user_123",
    "user_profile": {
        "goal": "hypertrophy",
        "days_per_week": 4,
        "experience": "intermediate",
        "gender": "male",
        "bodyweight_lb": 140.0
    },
    "constraints": {
        "session_length_minutes": 60,
        "equipment_access": "full_gym"
    }
}

SAMPLE_REQUEST_FEMALE_BEGINNER_WEIGHT_LOSS = {
    "user_id": "test_user_456",
    "user_profile": {
        "goal": "weight_loss",
        "days_per_week": 3,
        "experience": "beginner",
        "gender": "female",
        "bodyweight_lb": 130.0
    },
    "constraints": {
        "session_length_minutes": 45,
        "equipment_access": "dumbbells_only"
    }
}

SAMPLE_REQUEST_MALE_ADVANCED_STRENGTH = {
    "user_id": "test_user_789",
    "user_profile": {
        "goal": "strength",
        "days_per_week": 5,
        "experience": "advanced",
        "gender": "male",
        "bodyweight_lb": 180.0
    },
    "constraints": {
        "session_length_minutes": 75,
        "equipment_access": "full_gym"
    }
}


def test_plan_generation(api_url: str, payload: dict):
    """
    Test the plan generation endpoint.
    
    Args:
        api_url: Base URL of the API (e.g., "http://localhost:8000")
        payload: Request payload dict
    """
    endpoint = f"{api_url}/plans/generate"
    
    print(f"\n{'='*60}")
    print(f"Testing Plan Generation Endpoint")
    print(f"{'='*60}")
    print(f"\nEndpoint: {endpoint}")
    print(f"\nRequest Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        # Make request
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # OpenAI calls can take time
        )
        
        # Print response
        print(f"\nResponse Status: {response.status_code}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        # Check success
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("\n✅ Plan generated successfully!")
                plan = data.get('plan', {})
                print(f"\nPlan Overview:")
                overview = plan.get('overview', {})
                print(f"  - Goal: {overview.get('goal')}")
                print(f"  - Days/Week: {overview.get('days_per_week')}")
                print(f"  - Session Length: {overview.get('session_length_minutes')} min")
                print(f"  - Total Sessions: {len(plan.get('sessions', []))}")
            else:
                print("\n❌ Plan generation failed")
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Run test cases"""
    # Set your API URL here
    API_URL = "http://localhost:8000"
    
    print("\n" + "="*60)
    print("AI PLAN GENERATION TEST SUITE")
    print("="*60)
    
    # Test Case 1: Male, Intermediate, Hypertrophy
    print("\n\n📋 TEST CASE 1: Male, 140 lb, Intermediate, Hypertrophy, 4 days/week")
    test_plan_generation(API_URL, SAMPLE_REQUEST_MALE_INTERMEDIATE_HYPERTROPHY)
    
    # Test Case 2: Female, Beginner, Weight Loss
    print("\n\n📋 TEST CASE 2: Female, 130 lb, Beginner, Weight Loss, 3 days/week")
    test_plan_generation(API_URL, SAMPLE_REQUEST_FEMALE_BEGINNER_WEIGHT_LOSS)
    
    # Test Case 3: Male, Advanced, Strength
    print("\n\n📋 TEST CASE 3: Male, 180 lb, Advanced, Strength, 5 days/week")
    test_plan_generation(API_URL, SAMPLE_REQUEST_MALE_ADVANCED_STRENGTH)
    
    print("\n\n" + "="*60)
    print("Test suite complete")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
