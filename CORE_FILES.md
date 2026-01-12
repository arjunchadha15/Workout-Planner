# AI Plan Generation - Core Files for Backend Integration

## 🎯 Core Files (Production-Ready)

These are the essential files to integrate into your backend:

### **1. Core Service Files**
- `openai_service.py` - OpenAI API integration with structured prompts
- `ai_plan_generation_service.py` - Main orchestrator service
- `constraint_parser.py` - Natural language constraint parsing
- `exercise_selector.py` - Exercise selection with weight calculations
- `cardio_selector.py` - Cardio selection with goal-based defaults

### **2. Repository Files**
- `exercise_reference_repository.py` - Exercise database access
- `exercise_standard_repository.py` - Strength standards for weight calculation
- `cardio_reference_repository.py` - Cardio database access

### **3. Model Files**
- `base.py` - SQLAlchemy base
- `exercise_reference.py` - Exercise model
- `exercise_standard.py` - Strength standards model
- `cardio_reference.py` - Cardio model

### **4. Configuration**
- `config.py` - Environment configuration (API keys, DB URL)
- `requirements.txt` - Python dependencies

---

## 🧪 Test Files (For Development)

### **Keep These:**
- `test_plan_generation_clean.py` - **Main test suite** with 4 core tests
  - Basic plan generation
  - Constraint parsing (abs on leg days)
  - Equipment limitations
  - Age/experience adaptations

### **Optional/Legacy (Can Delete):**
- `test_openai_direct.py` - Direct OpenAI testing (redundant)
- `test_with_real_db.py` - Basic DB test (covered by clean test)
- `test_my_custom_plan.py` - Interactive test (useful for manual testing)
- `test_constraint_openai.py` - Constraint test (covered by clean test)
- `test_constraint_check.py` - Validation test (covered by clean test)
- `test_older_beginner.py` - Age test (covered by clean test)
- `test_young_advanced.py` - Age test (covered by clean test)
- `interactive_test.py` - Interactive CLI (useful for demos)

---

## 🗑️ Files to Remove

### **Mock/Deprecated:**
- `mock_database.py` - No longer used (using real DB)
- `cardio_templates.py` - Replaced by cardio database system
- `workout_plan_service.py` - Old service (check if still needed)

### **Documentation (Consolidate):**
- `README_AI_INTEGRATION.md`
- `IMPLEMENTATION_SUMMARY.md`
- `QUICK_START.md`
- `FILE_LIST.md`
- `INTERACTIVE_TEST_GUIDE.md`
- `WEIGHT_INTEGRATION_STATUS.md`
- `USER_PREFERENCES_NOTE.md`

Keep only this file (`CORE_FILES.md`) for reference.

### **Test Output Files:**
- `test_plan_output.json`
- `test_plan_real_db.json`
- `test_plan_older_beginner.json`
- `test_plan_young_advanced.json`
- `my_custom_plan.json`
- `workout_plan.md`

These are generated outputs, not source files.

---

## 🚀 Integration Steps

### **1. Backend Integration**
Copy these core files to your backend:
```
backend/
├── services/
│   ├── openai_service.py
│   ├── ai_plan_generation_service.py
│   ├── constraint_parser.py
│   ├── exercise_selector.py
│   └── cardio_selector.py
├── repositories/
│   ├── exercise_reference_repository.py
│   ├── exercise_standard_repository.py
│   └── cardio_reference_repository.py
└── models/
    ├── exercise_reference.py
    ├── exercise_standard.py
    └── cardio_reference.py
```

### **2. API Endpoint**
Current endpoint structure (from `plan_routes.py`):
```python
POST /api/plans/generate
Body:
{
  "user_id": "string",
  "age": int,
  "gender": "male|female",
  "body_weight_lb": float,
  "goal": "strength|hypertrophy|weight_loss|general_fitness",
  "experience": "beginner|intermediate|advanced",
  "days_per_week": int (3-6),
  "exercises_per_day": int,
  "equipment_access": "full_gym|dumbbells_only|home_gym|bodyweight_only",
  "split_type": "upper_lower|push_pull_legs|full_body|bro_split",
  "constraint_text": "optional natural language constraints"
}
```

### **3. Environment Variables**
Required in `.env`:
```
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=postgresql://...
```

### **4. Database Schema**
Required tables (already in your Supabase):
- `exercise_references` - Exercise library
- `exercise_standards` - Strength standards for weight calculation
- `cardio_references` - Cardio types (TODO: add to DB)

---

## 🔧 Dependencies

From `requirements.txt`:
```
openai>=1.12.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
```

---

## ⚠️ TODO Items

### **Cardio System:**
The cardio system currently uses `mock_cardio_database.py` because cardio types are not in the database yet. 

**Options:**
1. Add `cardio_references` table to database
2. Continue using mock (acceptable for now)
3. Hardcode cardio types in `cardio_selector.py`

Current mock includes:
- walking, treadmill, running, biking, swimming
- stairmaster, elliptical, row-machine, jump-rope, other

### **Constraint System:**
The constraint parser is production-ready and uses OpenAI to interpret natural language. Guardrails enforce:
- Equipment availability (filters DB queries)
- Split type validation (goal-based rules)
- Age/experience safety (exercise filtering)

---

## 📊 Test Coverage

Run `test_plan_generation_clean.py` to verify:
- ✅ Basic plan generation without constraints
- ✅ Constraint parsing (natural language → OpenAI interpretation)
- ✅ Equipment limitations (dumbbells only, etc.)
- ✅ Age/experience adaptations (safe exercises for older/beginner users)

All tests use **REAL database** (Supabase PostgreSQL) in **READ-ONLY** mode.

---

## 🎨 Frontend Integration (iOS)

The iOS onboarding flow collects:
1. Goal → determines split selection availability
2. Days per week → affects split options
3. Experience level → affects exercise selection
4. Gender → affects weight calculations
5. Body weight → required for weight calculations
6. Age → required for max heart rate (cardio zones)
7. Equipment access → filters exercise database
8. Split type → only shown for strength/hypertrophy
9. Exercises per day → workout volume
10. **Constraints (optional)** → natural language text input

After onboarding, send to `POST /api/plans/generate` with optional `constraint_text` field.

---

## 📝 Key Design Decisions

1. **Backend-Owned Parameters**: All logic lives in backend, not iOS
2. **Stateless OpenAI**: No conversation history, single API call
3. **Database Strictness**: Only exercises in DB are allowed (strict validation)
4. **Guardrails**: Safety rules cannot be overridden by user constraints
5. **Natural Language**: Constraints use OpenAI interpretation, not rigid parsing
6. **Weight Recommendations**: AI calculates weights for exercises without DB standards
7. **Zone-Based Cardio**: zone2/zone3/zone4 (no HIIT, no LISS labels)

---

## 🔍 File Cleanup Summary

**Remove these files:**
- All `test_*.py` except `test_plan_generation_clean.py` and optionally `test_my_custom_plan.py`
- `mock_database.py` (not used)
- `cardio_templates.py` (replaced)
- All `.json` output files (generated, not source)
- All `.md` docs except this file
- `workout_plan.md` (generated output)

**Keep for mock cardio (temporary):**
- `mock_cardio_database.py` - Still needed until cardio is in DB

**Production-ready files: 15 core files + config**
**Development files: 1-2 test files**

Total: ~17 files needed for full integration
