# 🚀 Quick Start Guide - OpenAI Workout Plan Generation

## Prerequisites
- Python 3.8+
- pip installed
- OpenAI API key (already in .env)
- Existing exercise database

## 5-Minute Setup

### Step 1: Install Dependencies (1 min)
```bash
cd "/Users/arjun/Desktop/Test/Ai Test"
pip install -r requirements.txt
```

### Step 2: Verify Configuration (30 sec)
Check that `.env` exists and contains:
```bash
cat .env
# Should show: OPENAI_API_KEY=sk-proj-...
```

### Step 3: Update Import Paths (2 min)
In these files, update imports to match your project:
- `ai_plan_generation_service.py` (lines 10-11)
- `plan_routes.py` (line 7)

Change:
```python
from app.repositories.exercise_reference_repository import ExerciseReferenceRepository
from app.database import get_db
```

To match your actual paths.

### Step 4: Register Blueprint (1 min)
In your Flask app (e.g., `app.py`):
```python
from plan_routes import plan_routes

app = Flask(__name__)
app.register_blueprint(plan_routes)
```

### Step 5: Test (30 sec)
```bash
python test_plan_generation.py
```

## First API Call

### Test with cURL:
```bash
curl -X POST http://localhost:8000/plans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
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

Expected response (truncated):
```json
{
  "success": true,
  "plan": {
    "plan_version": "v1",
    "overview": {
      "goal": "hypertrophy",
      "days_per_week": 4,
      "session_length_minutes": 60
    },
    "sessions": [...]
  }
}
```

## iOS Integration

### Update Your PlanGenerationService

Add this method:
```swift
func generateAIPlan(
    onboardingData: OnboardingData,
    completion: @escaping (Result<Plan, Error>) -> Void
) {
    let url = URL(string: "\(baseURL)/plans/generate")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let payload: [String: Any] = [
        "user_id": UserPreferences.shared.userId ?? "temp_user",
        "user_profile": [
            "goal": onboardingData.goal?.apiValue ?? "general_fitness",
            "days_per_week": onboardingData.daysPerWeek ?? 4,
            "experience": onboardingData.experienceLevel?.rawValue.lowercased() ?? "intermediate",
            "gender": onboardingData.gender?.rawValue.lowercased() ?? "male",
            "bodyweight_lb": Double(onboardingData.bodyWeight) ?? 150.0
        ],
        "constraints": [
            "session_length_minutes": onboardingData.sessionLengthMinutes,
            "equipment_access": onboardingData.equipmentAccess
        ]
    ]
    
    request.httpBody = try? JSONSerialization.data(withJSONObject: payload)
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            completion(.failure(error))
            return
        }
        
        guard let data = data else {
            completion(.failure(NSError(domain: "No data", code: -1)))
            return
        }
        
        // Parse and return plan
        do {
            let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
            if let planData = json?["plan"] as? [String: Any] {
                // Convert to your Plan model
                // completion(.success(plan))
            }
        } catch {
            completion(.failure(error))
        }
    }.resume()
}
```

### Call from GeneratingPlanInteractivePage

Replace existing plan generation call:
```swift
planService.generateAIPlan(onboardingData: onboardingData) { result in
    switch result {
    case .success(let plan):
        // Handle success
    case .failure(let error):
        // Handle error
    }
}
```

## Goal Values Reference

| UI Display | API Value |
|-----------|-----------|
| Strength Gain | `strength` |
| Hypertrophy | `hypertrophy` |
| Weight Loss | `weight_loss` |
| General Fitness | `general_fitness` |

## Equipment Access Values

| Value | Exercises Available |
|-------|-------------------|
| `full_gym` | Barbell, dumbbell, machine, cable, bodyweight |
| `dumbbells_only` | Dumbbell, bodyweight |
| `home_gym` | Dumbbell, bodyweight, bands |
| `bodyweight_only` | Bodyweight only |

## Common Issues

### ❌ "OPENAI_API_KEY not found"
**Fix:** Ensure `.env` file is in the same directory as `config.py`

### ❌ Import errors
**Fix:** Update import paths in new files to match your structure

### ❌ "No exercises available"
**Fix:** Check your exercise database has exercises with the required equipment

### ❌ OpenAI timeout
**Fix:** Increase timeout in request or check OpenAI API status

## What Gets Generated

For a typical 4-day hypertrophy plan, OpenAI will generate:
- ✅ 4 workout sessions
- ✅ 4-6 exercises per session
- ✅ Sets, reps, rest periods for each exercise
- ✅ Coaching notes
- ✅ Optional cardio (if appropriate for goal)
- ✅ Balanced muscle group distribution

## Next Steps

1. ✅ Test backend with `test_plan_generation.py`
2. ✅ Update iOS PlanGenerationService
3. ✅ Test iOS to backend connection
4. ✅ Update plan storage logic
5. ✅ Test full user flow

## Need Help?

Check these files:
- **IMPLEMENTATION_SUMMARY.md** - Overview of all changes
- **README_AI_INTEGRATION.md** - Detailed documentation
- **test_plan_generation.py** - Example API calls

---

**You're all set! Start testing with the Python test script.** 🎉
