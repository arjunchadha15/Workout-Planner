# AI-Powered Workout Plan Generation - Integration Guide

## Overview

This implementation integrates OpenAI for personalized workout plan generation while maintaining the existing architecture. The backend owns the parameter flow, OpenAI is stateless, and plans are generated via a single endpoint call.

## Architecture

### Key Principles
- **Backend-Owned Parameters**: All user profile and constraints are managed server-side
- **Stateless OpenAI**: Each API call is independent with full context
- **Freedom Within a Box**: OpenAI chooses from a curated, prioritized exercise list
- **Single Endpoint Generation**: Complete plan generated in one POST request

## Files Changed/Added

### iOS Frontend Changes

#### 1. `OnboardingData.swift` (MODIFIED)
**Changes:**
- Added `Goal` enum with 4 options: Strength, Hypertrophy, Weight Loss, General Fitness
- Added `goal` property to store user's fitness goal
- Added `sessionLengthMinutes` (default: 60) for workout duration constraint
- Added `equipmentAccess` (default: "full_gym") for equipment availability
- Updated `isComplete()` to require goal selection

#### 2. `GoalSelectionPage.swift` (NEW)
**Purpose:** New onboarding page to collect user's fitness goal
**Features:**
- 4 goal options with emojis and descriptions
- Follows existing OnboardingLayout pattern
- Uses OnboardingSelectionButton components

#### 3. `NewOnboardingView.swift` (MODIFIED)
**Changes:**
- Updated totalPages from 4 to 5
- Added GoalSelectionPage as page 3 (after Gender, before Body Weight)
- Updated page tagging to accommodate new page
- Saves goal to UserPreferences on completion

#### 4. `WorkoutDurationInteractivePage.swift` (MODIFIED)
**Changes:**
- Maps workout duration selections to `sessionLengthMinutes`:
  - Short (30-45 min) → 40 minutes
  - Medium (45-60 min) → 55 minutes
  - Long (60-90 min) → 75 minutes

### Backend Files

#### 5. `.env` (NEW)
**Purpose:** Environment configuration file
**Contains:**
- `OPENAI_API_KEY` - Your OpenAI API key (REQUIRED)
- Database URL, API host/port (optional)

**⚠️ SECURITY:** This file contains your API key. It is already added to `.gitignore`.

#### 6. `.gitignore` (NEW)
**Purpose:** Prevents sensitive files from being committed
**Includes:** .env, __pycache__, *.pyc, etc.

#### 7. `config.py` (NEW)
**Purpose:** Centralized configuration management
**Features:**
- Loads environment variables from .env file
- Validates OpenAI API key presence and format
- Provides OpenAI configuration (model, temperature, max_tokens)
- Configurable via environment variables

#### 8. `cardio_templates.py` (NEW)
**Purpose:** Cardio workout template repository
**Features:**
- 5 predefined cardio templates (Zone 2, HIIT, LISS, Active Recovery, Conditioning)
- Each template has duration, intensity, and suitable goals
- Can filter templates by fitness goal
- Provides simplified summaries for OpenAI prompt

#### 9. `exercise_selector.py` (NEW)
**Purpose:** Exercise ranking and filtering logic
**Features:**
- Filters exercises by equipment access (full_gym, dumbbells_only, home_gym, bodyweight_only)
- Ranks exercises based on:
  - Core compound movements (highest priority)
  - Goal-specific preferences (equipment, rep ranges)
  - Availability of strength standards data
- Fetches suggested weights from exercise standards DB
- Returns prioritized list (default: top 50 exercises)

#### 10. `openai_service.py` (NEW)
**Purpose:** OpenAI API integration and prompt engineering
**Features:**
- Constructs detailed system prompt with programming rules for each goal
- Builds user-specific prompt with profile, constraints, and allowed exercises
- Calls OpenAI Chat Completions API with JSON mode
- Validates generated plans (session count, exercise IDs)
- Goal-specific programming rules:
  - **Strength**: 3-6 reps, 3-5 min rest, heavy compounds, minimal cardio
  - **Hypertrophy**: 8-12 reps, 60-90s rest, balanced compound/isolation, light cardio
  - **Weight Loss**: 12-15 reps, 30-60s rest, circuit-friendly, required cardio (20-30 min)
  - **General Fitness**: 8-12 reps, 60-90s rest, functional movements, optional cardio

#### 11. `ai_plan_generation_service.py` (NEW)
**Purpose:** Main orchestrator for AI plan generation
**Features:**
- Validates required user profile fields
- Coordinates exercise selection
- Fetches goal-appropriate cardio templates
- Calls OpenAI service
- Enriches plan with exercise metadata
- Returns complete plan with generation metadata

#### 12. `plan_routes.py` (NEW)
**Purpose:** Flask API endpoint for plan generation
**Endpoints:**
- `POST /plans/generate` - Generate workout plan
- `GET /plans/health` - Health check

**Request Format:**
```json
{
  "user_id": "string",
  "user_profile": {
    "goal": "strength|hypertrophy|weight_loss|general_fitness",
    "days_per_week": 4,
    "experience": "beginner|intermediate|advanced",
    "gender": "male|female",
    "bodyweight_lb": 140.0
  },
  "constraints": {
    "session_length_minutes": 60,
    "equipment_access": "full_gym"
  }
}
```

#### 13. `requirements.txt` (NEW)
**Purpose:** Python package dependencies
**Key Packages:**
- `openai>=1.12.0` - OpenAI API client
- `flask>=2.3.0` - Web framework
- `sqlalchemy>=2.0.0` - Database ORM
- `python-dotenv>=1.0.0` - Environment variable loader

#### 14. `test_plan_generation.py` (NEW)
**Purpose:** Test script with sample requests
**Features:**
- 3 pre-configured test cases
- Sample requests for different user profiles
- Demonstrates API usage
- Formatted output for easy debugging

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd "Ai Test"
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

The OpenAI API key is already set in the `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

**⚠️ Important:** Get your API key from https://platform.openai.com/api-keys. Never commit this to version control.

### 3. Integrate with Existing Flask App

In your main Flask app file (e.g., `app.py`), register the blueprint:

```python
from plan_routes import plan_routes

app = Flask(__name__)
app.register_blueprint(plan_routes)
```

### 4. Update Database Imports

The code assumes certain import paths. Update these in the new files:

In `ai_plan_generation_service.py` and `plan_routes.py`, adjust:
```python
from app.repositories.exercise_reference_repository import ExerciseReferenceRepository
from app.repositories.exercise_standard_repository import ExerciseStandardRepository
from app.database import get_db
```

Replace `app.` with your actual module path.

## Testing

### Run Test Script

```bash
cd "Ai Test"
python test_plan_generation.py
```

This will test 3 scenarios:
1. Male, 140 lb, Intermediate, Hypertrophy, 4 days/week
2. Female, 130 lb, Beginner, Weight Loss, 3 days/week
3. Male, 180 lb, Advanced, Strength, 5 days/week

### Manual Testing with cURL

```bash
curl -X POST http://localhost:8000/plans/generate \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## Plan JSON Schema

The generated plan follows this structure:

```json
{
  "plan_version": "v1",
  "overview": {
    "goal": "hypertrophy",
    "days_per_week": 4,
    "session_length_minutes": 60,
    "notes": "4-day hypertrophy split focusing on muscle growth"
  },
  "sessions": [
    {
      "day_index": 0,
      "title": "Upper Body - Push",
      "blocks": [
        {
          "type": "strength",
          "items": [
            {
              "exercise_id": "bench-press",
              "exercise_name": "Bench Press",
              "category": "chest",
              "equipment": "barbell",
              "sets": 4,
              "reps": "8-10",
              "rest_seconds": 90,
              "notes": "Focus on controlled eccentric"
            }
          ]
        },
        {
          "type": "cardio",
          "items": [
            {
              "exercise_id": "zone2_steady_v1",
              "sets": 1,
              "reps": "20 min",
              "rest_seconds": 0,
              "notes": "Optional - Zone 2 steady state"
            }
          ]
        }
      ]
    }
  ]
}
```

## Integration with iOS App

### Update PlanGenerationService

In your existing iOS `PlanGenerationService`, add a method to call the new AI endpoint:

```swift
func generateAIPlan(
    goal: String,
    daysPerWeek: Int,
    experience: String,
    gender: String,
    bodyweight: Double,
    sessionLength: Int,
    equipment: String,
    completion: @escaping (Result<Plan, Error>) -> Void
) {
    let url = URL(string: "\(baseURL)/plans/generate")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let payload: [String: Any] = [
        "user_id": currentUserId,
        "user_profile": [
            "goal": goal,
            "days_per_week": daysPerWeek,
            "experience": experience,
            "gender": gender,
            "bodyweight_lb": bodyweight
        ],
        "constraints": [
            "session_length_minutes": sessionLength,
            "equipment_access": equipment
        ]
    ]
    
    request.httpBody = try? JSONSerialization.data(withJSONObject: payload)
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        // Handle response
    }.resume()
}
```

### Update GeneratingPlanInteractivePage

Modify the plan generation call to use the new goal and constraints:

```swift
planService.generateAIPlan(
    goal: onboardingData.goal?.apiValue ?? "general_fitness",
    daysPerWeek: onboardingData.daysPerWeek ?? 4,
    experience: onboardingData.experienceLevel?.rawValue.lowercased() ?? "intermediate",
    gender: onboardingData.gender?.rawValue.lowercased() ?? "male",
    bodyweight: Double(onboardingData.bodyWeight) ?? 150.0,
    sessionLength: onboardingData.sessionLengthMinutes,
    equipment: onboardingData.equipmentAccess
) { result in
    // Handle result
}
```

## Goal-Specific Programming Details

### Strength Goal
- **Rep Range:** 3-6 reps
- **Rest Periods:** 3-5 minutes for compounds, 2-3 for accessories
- **Exercise Selection:** Prioritizes barbell compounds (squat, bench, deadlift, overhead press)
- **Cardio:** Minimal or none (optional active recovery)
- **Programming Notes:** Lower reps, higher weight, focus on neural adaptations

### Hypertrophy Goal
- **Rep Range:** 8-12 reps
- **Rest Periods:** 60-90 seconds
- **Exercise Selection:** Balanced mix of compounds and isolation
- **Cardio:** Light (10-15 min LISS post-workout, optional)
- **Programming Notes:** Moderate weight, higher volume, time under tension

### Weight Loss Goal
- **Rep Range:** 12-15 reps
- **Rest Periods:** 30-60 seconds (keeps heart rate elevated)
- **Exercise Selection:** Circuit-friendly exercises, full-body movements
- **Cardio:** Required (20-30 min HIIT or steady-state per session)
- **Programming Notes:** Higher reps, shorter rest, metabolic focus

### General Fitness Goal
- **Rep Range:** 8-12 reps
- **Rest Periods:** 60-90 seconds
- **Exercise Selection:** Functional compound movements
- **Cardio:** Optional but recommended (15-20 min moderate intensity)
- **Programming Notes:** Balanced approach for overall health and fitness

## Equipment Access Options

- **`full_gym`**: Barbell, dumbbell, machine, cable, bodyweight
- **`dumbbells_only`**: Dumbbell and bodyweight exercises
- **`home_gym`**: Dumbbell, bodyweight, and resistance bands
- **`bodyweight_only`**: Bodyweight exercises only

## Troubleshooting

### OpenAI API Key Error
**Error:** "OPENAI_API_KEY not found"
**Solution:** Ensure the `.env` file is in the same directory as `config.py` and contains the API key.

### No Exercises Available
**Error:** "No exercises available for the given constraints"
**Solution:** Check your exercise database has exercises with the required equipment types.

### OpenAI Rate Limit
**Error:** "Rate limit exceeded"
**Solution:** OpenAI has rate limits. Wait a moment and try again, or upgrade your API plan.

### Import Errors
**Error:** "ModuleNotFoundError: No module named 'app'"
**Solution:** Update import paths in the new files to match your project structure.

## Future Enhancements

1. **Constraints Enrichment (Step B)**: Implement AI-based chat to extract structured constraints
2. **Exercise Swap**: Allow users to swap individual exercises
3. **Progressive Overload**: Implement automatic weight progression tracking
4. **Deload Weeks**: Add periodic deload planning
5. **Exercise Video Integration**: Link exercises to tutorial videos
6. **Nutrition Integration**: Add meal planning based on goals

## Support

For questions or issues, refer to:
- OpenAI API Docs: https://platform.openai.com/docs
- Exercise Database: Check `exercise_reference_repository.py`
- Strength Standards: Check `exercise_standard_repository.py`

---

**Last Updated:** January 4, 2026
**Version:** 1.0.0
