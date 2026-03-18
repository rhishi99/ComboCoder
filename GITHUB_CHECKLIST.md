# GitHub Publishing Checklist

Use this checklist before pushing FreeAgentDev to GitHub.

---

## ✅ Pre-Push Verification

### Security Check
- [ ] No `config.yaml` file in repo (check: `git status`)
- [ ] No `.env` file in repo (check: `git status`)
- [ ] `.gitignore` contains all sensitive files
  - [ ] `.env*` patterns
  - [ ] `config.yaml` entries
  - [ ] `progress/` folder
  - [ ] `workspace/` folder
- [ ] Example files exist and have no real secrets:
  - [ ] `config.example.yaml` (with placeholder keys only)
  - [ ] `.env.example` (with placeholder format only)

**Verification command**:
```bash
# Nothing secret should be listed
git status --short
```

### Documentation Check
- [ ] `README.md` exists and is complete
- [ ] `USERS_GUIDE.md` exists and is detailed (70KB+)
- [ ] `ONBOARDING.md` exists
- [ ] `QUICK_REFERENCE.md` exists
- [ ] `config.example.yaml` is correct template
- [ ] `.env.example` is correct template

### Code Quality Check
- [ ] No hardcoded API keys in any Python files
- [ ] No hardcoded secrets in any configuration files
- [ ] All imports work: `pip install -r requirements.txt` succeeds
- [ ] Tests can be run: `python -m pytest tests/ -v`

**Verification command**:
```bash
# Search for hardcoded keys (should find 0 results)
grep -r "gsk_" freeagentdev/
grep -r "nvapi-" freeagentdev/
grep -r "sk-or-" freeagentdev/
```

---

## ✅ Setup Reproduction Check

Before publishing, verify a fresh user can set up from scratch:

```bash
# 1. Create a test directory
mkdir test_repo
cd test_repo

# 2. Clone your repo (or copy files)
git clone <your-repo-url>
# OR
cp -r ../ComboCoder .
cd ComboCoder

# 3. Verify templates exist
ls config.example.yaml
ls .env.example

# 4. Create fresh venv
python -m venv .venv

# 5. Activate (choose your OS)
# Windows: .venv\Scripts\activate.bat
# Mac/Linux: source .venv/bin/activate

# 6. Install dependencies
pip install -r requirements.txt

# 7. Verify no secrets in repo
git status
# Should show NO:
# - config.yaml
# - .env files
# - progress/ folder
# - workspace/ folder
```

All checks should pass ✅

---

## ✅ GitHub Repository Setup

### Create Repository
- [ ] Create new repository on GitHub
- [ ] Repository name: `ComboCoder` or `FreeAgentDev`
- [ ] Description: "Multi-provider AI software development agent with automatic fallback"
- [ ] Public: Yes
- [ ] Initialize with: None (we'll push existing repo)

### Add Topics (Optional but Recommended)
- [ ] `ai`
- [ ] `coding-assistant`
- [ ] `llm`
- [ ] `multi-provider`
- [ ] `automation`
- [ ] `python`

### Add Repository Links
- [ ] Homepage URL: (if you have one)
- [ ] README: Check (GitHub will auto-display it)

---

## ✅ First Push Commands

```bash
# 1. Navigate to repo directory
cd path/to/ComboCoder

# 2. Initialize git (if not already done)
git init

# 3. Add remote
git remote add origin https://github.com/YOUR_USERNAME/ComboCoder.git

# 4. Verify nothing secret is staged
git status
# Should NOT show: config.yaml, .env, progress, workspace

# 5. Stage all safe files
git add .

# 6. Create initial commit with Copilot trailer
git commit -m "Initial commit: Multi-provider AI coding agent

- Supports 8+ LLM providers with automatic fallback
- 4-agent workflow (Planner, Architect, Engineer, Reviewer)
- Automatic rate limit handling
- Free tier API keys supported
- Comprehensive documentation and setup guide

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

# 7. Push to GitHub
git branch -M main
git push -u origin main
```

---

## ✅ Post-Push Verification

After pushing, verify everything is correct:

1. **Visit your GitHub repo URL** - Should see:
   - [ ] README.md rendered nicely
   - [ ] `USERS_GUIDE.md` link visible
   - [ ] All markdown files listed
   - [ ] No `config.yaml` file
   - [ ] No `.env` file
   - [ ] No `progress/` folder
   - [ ] No `workspace/` folder

2. **Check file permissions** - Should see:
   - [ ] `freeagent.py` is readable
   - [ ] `requirements.txt` is readable
   - [ ] All `.md` files are readable

3. **Verify template files** - Can see:
   - [ ] `config.example.yaml` (with example keys)
   - [ ] `.env.example` (with example format)

---

## ✅ Documentation Visibility

Users should easily find:

- [ ] **README.md** on repo home page
- [ ] **USERS_GUIDE.md** link in README (table of contents + special section)
- [ ] **QUICK_REFERENCE.md** link in README or USERS_GUIDE
- [ ] **ONBOARDING.md** link in README
- [ ] **config.example.yaml** as reference for setup

---

## 🚀 Launch Checklist (After Pushing)

After successful push:

- [ ] Share repo link with users
- [ ] Provide link to `USERS_GUIDE.md` for setup
- [ ] Provide `QUICK_REFERENCE.md` for experienced users
- [ ] Monitor for questions/issues
- [ ] Update README if needed based on feedback

---

## 📋 Security Audit (Final)

Run these commands in the **cloned repo** (from GitHub) to verify security:

```bash
# 1. Check for any secrets
git log --all --oneline
git show HEAD  # Should show only safe files

# 2. Verify .gitignore is working
git check-ignore config.yaml        # Should return: config.yaml
git check-ignore .env               # Should return: .env
git check-ignore README.md          # Should return nothing (file should be included)

# 3. List all committed files (no secrets should appear)
git ls-tree -r HEAD --name-only
```

**Result**: No API keys, no `.env` files, no `config.yaml` files should be committed.

---

## 📝 Commit History

Your repo should have a clean history like:

```
* Initial commit: Multi-provider AI coding agent
  ├─ freeagent.py
  ├─ requirements.txt
  ├─ README.md
  ├─ USERS_GUIDE.md
  ├─ QUICK_REFERENCE.md
  ├─ config.example.yaml
  ├─ .env.example
  ├─ .gitignore
  ├─ freeagentdev/
  ├─ tests/
  └─ ... (no secrets)
```

---

## ⚠️ If You Need to Start Over

If you accidentally committed secrets:

```bash
# 1. Do NOT push to GitHub yet!

# 2. Remove files from git history
git rm --cached config.yaml
git rm --cached .env
git rm --cached freeagentdev/config.yaml

# 3. Update .gitignore to include them

# 4. Commit the removal
git add .gitignore
git commit -m "Remove accidentally committed config files"

# 5. Now safe to push
git push -u origin main
```

---

## ✅ Final Sign-Off

Before pushing to GitHub, check:

```bash
echo "=== SECURITY CHECK ==="
git status --short | grep -E "config.yaml|\.env"
# Should return NOTHING

echo "=== DOCUMENTATION CHECK ==="
ls README.md USERS_GUIDE.md QUICK_REFERENCE.md config.example.yaml .env.example
# All files should exist

echo "=== READY TO PUSH ==="
git log --oneline -1
# Should show your commit
```

If all checks pass ✅ → You're ready to push!

---

## 📊 Summary

Your repo is ready when:

- ✅ No API keys in any committed files
- ✅ All example/template files exist with no real secrets
- ✅ Comprehensive documentation included
- ✅ .gitignore properly configured
- ✅ Tests run successfully
- ✅ Fresh setup works from scratch

**Result**: Users can clone, follow USERS_GUIDE.md, and start coding immediately! 🚀
