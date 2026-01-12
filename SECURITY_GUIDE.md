# 🔒 Secure API Key Setup Guide

## ✅ Current Status
Your API key is **already secure**! Here's what's in place:

1. ✅ API key stored in `.env` file (not hardcoded)
2. ✅ `.env` is in `.gitignore` (won't be committed)
3. ✅ Code uses `os.getenv('OPENAI_API_KEY')` to read it
4. ✅ `.env.example` template created for others

---

## 🚀 How to Push to Repository

### Step 1: Verify .gitignore
Your `.gitignore` already includes:
```
.env
*.pyc
__pycache__/
```

This ensures `.env` will **NEVER** be committed to git.

### Step 2: Push to Repository
```bash
cd "/Users/arjun/Desktop/Test/Ai Test"

# Initialize git (if not already done)
git init

# Add all files (except .env - it's in .gitignore)
git add .

# Commit
git commit -m "Add AI workout plan generation system"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/your-repo.git

# Push
git push -u origin main
```

**Result:** Your code will be pushed, but `.env` with the API key will **NOT** be included.

---

## 🔗 Integration with Main App

### Option 1: Separate Repo → Main App Integration

**Step A: In Your AI Repo**
```bash
# Create a clean Python package structure
# (Already done - you have all the necessary files)
```

**Step B: In Your Main App**
```bash
# Add as a git submodule
git submodule add https://github.com/yourusername/ai-workout-planner.git ai_service

# Or install as a package
pip install git+https://github.com/yourusername/ai-workout-planner.git
```

**Step C: Set Environment Variable in Main App**
```bash
# In your main app's .env file
OPENAI_API_KEY=sk-your-actual-key-here
```

---

### Option 2: Merge Into Main App (Recommended)

**Step A: Copy Files to Main App**
```bash
# In your main app directory
mkdir -p services/ai_workout_planner
cp -r "/Users/arjun/Desktop/Test/Ai Test/"*.py services/ai_workout_planner/
```

**Step B: Add API Key to Main App's .env**
```bash
# In your main app's .env file
OPENAI_API_KEY=sk-your-actual-key-here
```

**Step C: Update Main App's .gitignore**
Make sure your main app's `.gitignore` includes:
```
.env
.env.local
.env.production
*.pyc
__pycache__/
```

---

## 🔐 Best Practices for Production

### 1. Use Environment Variables (Done ✅)
```python
# config.py - Already implemented correctly
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

### 2. Never Commit .env File (Done ✅)
- `.env` is in `.gitignore`
- Use `.env.example` as template

### 3. Different Keys for Different Environments
```bash
# Development .env
OPENAI_API_KEY=sk-dev-key-here

# Production .env (on server)
OPENAI_API_KEY=sk-prod-key-here
```

### 4. For Production Deployment

**Option A: Set Environment Variables on Server**
```bash
# On your production server
export OPENAI_API_KEY=sk-prod-key-here

# Or add to systemd service file, docker-compose, etc.
```

**Option B: Use Secret Management Service**
- AWS Secrets Manager
- Google Cloud Secret Manager
- Azure Key Vault
- Heroku Config Vars
- Vercel Environment Variables

---

## 🧪 For Team Members / Collaborators

When someone clones the repo:

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Copy .env.example to .env**
   ```bash
   cp .env.example .env
   ```

3. **Add their own API key**
   ```bash
   # Edit .env file
   OPENAI_API_KEY=sk-their-own-api-key-here
   ```

4. **Install dependencies and run**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

---

## ⚠️ Security Checklist

Before pushing to GitHub:

- [x] `.env` is in `.gitignore`
- [x] No hardcoded API keys in code
- [x] `.env.example` template created (without real keys)
- [ ] Check git history doesn't contain old API keys
- [ ] Review all Python files for accidental key exposure

**To check git history:**
```bash
git log --all --full-history --source --pretty=oneline -S "sk-"
```

If you find any keys in history, you'll need to:
1. Rotate the API key (get a new one from OpenAI)
2. Clean git history (using git filter-branch or BFG Repo-Cleaner)

---

## 📝 Quick Commands

```bash
# Check if .env is ignored
git check-ignore .env
# Should output: .env

# Check what will be committed
git status

# See what's in .gitignore
cat .gitignore

# Make sure .env is never tracked
git rm --cached .env  # if accidentally added
git commit -m "Remove .env from tracking"
```

---

## ✅ You're Ready!

Your setup is already secure. To push to a repository:

1. Create a repo on GitHub (keep it private or public - both are safe)
2. Run the git commands from Step 2 above
3. Your API key stays local in `.env` file
4. Other developers use `.env.example` as a template

**The .env file will NEVER be pushed to GitHub!** ✅
