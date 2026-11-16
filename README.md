# Repple AI Workout Planner

**The backend service that generates personalized workout plans for [Repple](https://github.com/arjunchadha15/Repple-Landing-Page), the gamified fitness app I founded for college students.**

During onboarding, a new Repple user picks a goal, how many days a week they can train, how long their sessions are, and what equipment they have. This service turns that into a full weekly plan in one API call.

## The approach: freedom within a box

Letting an LLM write a workout plan from scratch is risky. It can invent exercises, ignore equipment, or program something unsafe for a beginner. So the backend owns the rules and the model only makes choices inside them.

1. **The backend builds the box.** `exercise_selector.py` filters the exercise database by equipment and ranks it by goal, with core compound lifts first. `cardio_selector.py` does the same for conditioning.
2. **The model chooses inside it.** `openai_service.py` sends the user's profile and that curated, prioritized list to OpenAI and asks for a plan in strict JSON. It can only pick from exercises the backend allowed.
3. **Users can speak naturally.** `constraint_parser.py` turns free-text requests like "I only have dumbbells and a pull-up bar" or "add abs at the end of every workout" into structured constraints, with guardrails so a request can never override safety rules for age and experience.
4. **The backend validates the result** before it goes back to the app.

## API

`POST /plans/generate`

```json
{
  "user_id": "string",
  "user_profile": {
    "goal": "strength | hypertrophy | weight_loss | general_fitness",
    "days_per_week": 4,
    "experience": "beginner | intermediate | advanced",
    "gender": "male | female",
    "bodyweight_lb": 150.0
  },
  "constraints": {
    "session_length_minutes": 60,
    "equipment_access": "full_gym | dumbbells_only | home_gym | bodyweight_only"
  }
}
```

`GET /plans/health` returns the service status.

## Testing across real user types

`test_comprehensive_suite.py` generates plans for ten personas (an advanced young lifter, an older beginner, a dumbbells-only user, a push/pull/legs split with abs, and more), and `review_plans.py` checks each one. The generated plans are the `review_*.json` files, summarized in `review_summary.json`.

## Tech stack

Python, Flask, SQLAlchemy, OpenAI API (JSON mode), pytest. The iOS onboarding screens that call this service live in the Repple app.

## Running locally

```bash
pip install -r requirements.txt
cp .env.example .env      # add OPENAI_API_KEY
python app.py             # http://localhost:8000
python interactive_test.py
```

Design notes and earlier working docs are in [`docs/`](docs/).

---

Built by [Arjun Chadha](https://www.linkedin.com/in/arjun-chadha-7164221b1).
