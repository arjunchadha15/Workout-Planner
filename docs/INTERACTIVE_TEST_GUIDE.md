# 🎮 Interactive Terminal Test - How to Use

## Quick Start

### 1. Run the Interactive Test

```bash
cd "/Users/arjun/Desktop/Test/Ai Test"
python3 interactive_test.py
```

### 2. Answer the Questions

The script will ask you questions one by one:

```
👤 User Profile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What's your primary fitness goal?
  1. Strength Gain
  2. Hypertrophy (Muscle Building)
  3. Weight Loss
  4. General Fitness

Your choice: 2

How many days per week can you train?
  1. 3
  2. 4
  3. 5
  4. 6
  (Press Enter for default: 4)

Your choice: [just press Enter for default]
```

### 3. Review Your Answers

Before calling the API, you'll see a summary:

```
📋 Your Profile Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: Hypertrophy (Muscle Building) (hypertrophy)
Days/Week: 4
Experience: Intermediate (1-3 years) (intermediate)
Gender: Male (male)
Bodyweight: 140.0 lb
Session Length: 60 minutes
Equipment: Full Gym (full_gym)

✅ Generate plan with these settings? (y/n) [y]:
```

### 4. Get Your Plan

The API will generate your plan and display it:

```
✅ SUCCESS! Plan generated successfully!

📊 PLAN OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Goal: hypertrophy
Days per Week: 4
Session Length: 60 minutes
Notes: 4-day hypertrophy split...

🗓️  WORKOUT SESSIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session 1: Upper Body - Push
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRENGTH BLOCK:
─────────────────────────────────────────────

• Bench Press
  Sets: 4 | Reps: 8-10 | Rest: 90s
  Notes: Focus on controlled eccentric
  
• Incline Dumbbell Press
  Sets: 3 | Reps: 10-12 | Rest: 75s
  ...
```

## Features

### ✨ Interactive Input
- Type your answers to each question
- Press Enter for default values
- Number-based selection (1, 2, 3, etc.)

### 🎯 Smart Defaults
- API URL: `http://localhost:8000`
- User ID: `test_user`
- Days/week: `4`
- Session length: `60 minutes`
- Equipment: `Full Gym`

### 💾 Save Option
After viewing the plan, you can save it to a JSON file:
```
💾 Save full plan to JSON file? (y/n) [n]: y
✅ Plan saved to: workout_plan_test_user_hypertrophy.json
```

## Example Session

```bash
$ python3 interactive_test.py

============================================================
  🏋️  AI WORKOUT PLAN GENERATOR - Interactive Test
============================================================

This will guide you through generating a personalized workout plan.
You'll answer a few questions, then we'll call the API.

API Configuration
────────────────────────────────────────
Enter API URL [http://localhost:8000]: 

Enter user ID (or press Enter for 'test_user') [test_user]: 

👤 User Profile
────────────────────────────────────────

What's your primary fitness goal?
  1. Strength Gain
  2. Hypertrophy (Muscle Building)
  3. Weight Loss
  4. General Fitness

Your choice: 2

How many days per week can you train?
  1. 3
  2. 4
  3. 5
  4. 6
  (Press Enter for default: 4)

Your choice: 

What's your experience level?
  1. Beginner (< 1 year)
  2. Intermediate (1-3 years)
  3. Advanced (3+ years)

Your choice: 2

What's your gender?
  1. Male
  2. Female

Your choice: 1

What's your bodyweight (in pounds)? [150]: 140

⚙️  Workout Constraints
────────────────────────────────────────

How long should each workout be?
  1. 30 minutes (Quick)
  2. 45 minutes (Short)
  3. 60 minutes (Standard)
  4. 75 minutes (Long)
  5. 90 minutes (Extended)
  (Press Enter for default: 60 minutes (Standard))

Your choice: 

What equipment do you have access to?
  1. Full Gym (barbell, dumbbell, machines, cables)
  2. Dumbbells Only (dumbbell + bodyweight)
  3. Home Gym (dumbbells + bands + bodyweight)
  4. Bodyweight Only
  (Press Enter for default: Full Gym (barbell, dumbbell, machines, cables))

Your choice: 

📋 Your Profile Summary
────────────────────────────────────────
Goal: Hypertrophy (Muscle Building) (hypertrophy)
Days/Week: 4
Experience: Intermediate (1-3 years) (intermediate)
Gender: Male (male)
Bodyweight: 140.0 lb
Session Length: 60 minutes
Equipment: Full Gym (barbell, dumbbell, machines, cables) (full_gym)

✅ Generate plan with these settings? (y/n) [y]: y

🚀 Calling API...
────────────────────────────────────────
Endpoint: http://localhost:8000/plans/generate

⏳ Generating your personalized workout plan...
   (This may take 10-30 seconds with OpenAI)

[... plan generated ...]
```

## Troubleshooting

### Error: "Could not connect"
```
❌ CONNECTION ERROR
Could not connect to http://localhost:8000
Make sure your API server is running!
```

**Solution:** Start your Flask API server first:
```bash
python app.py  # or whatever your main Flask file is
```

### Error: "Request timeout"
```
❌ REQUEST TIMEOUT
The API took too long to respond (>60s)
```

**Solution:** OpenAI sometimes takes longer. Just run the script again.

### Error: "Invalid number"
```
❌ Please enter a number between 1 and 4
```

**Solution:** Type a valid number from the options shown.

## Tips

1. **Use defaults:** Just press Enter to accept default values
2. **Cancel anytime:** Press `Ctrl+C` to exit
3. **Save plans:** Type `y` when asked to save the plan as JSON
4. **Try different goals:** Run multiple times with different settings
5. **Test variations:** Try different experience levels, equipment, etc.

## What Gets Tested

✅ API connectivity  
✅ Request payload formatting  
✅ OpenAI plan generation  
✅ Goal-specific programming  
✅ Equipment filtering  
✅ Session length constraints  
✅ Experience-appropriate weights  
✅ Response parsing  
✅ Error handling  

## Next: Test Different Scenarios

### Scenario 1: Beginner Weight Loss
- Goal: Weight Loss
- Days: 3
- Experience: Beginner
- Bodyweight: 130 lb
- Session: 45 minutes
- Equipment: Dumbbells Only

### Scenario 2: Advanced Strength
- Goal: Strength Gain
- Days: 5
- Experience: Advanced
- Bodyweight: 180 lb
- Session: 75 minutes
- Equipment: Full Gym

### Scenario 3: Intermediate General Fitness
- Goal: General Fitness
- Days: 4
- Experience: Intermediate
- Bodyweight: 150 lb
- Session: 60 minutes
- Equipment: Home Gym

---

**Ready to test? Run: `python3 interactive_test.py`** 🚀
