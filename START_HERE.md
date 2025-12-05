# 🚀 START HERE - RAKEZ Lead Scoring Model

## ⚠️ Important: Run from Project Root!

The `setup.py` and `start.py` scripts are in the **root directory**, not in subdirectories.

## 📍 Current Location Check

You're currently in: `03_api/` directory

**You need to be in**: `rakez-lead-scoring-deployment/` (root directory)

## ✅ Quick Fix

### Option 1: Navigate to Root (Recommended)

```bash
# Go back to root directory
cd ..

# Now you're in: rakez-lead-scoring-deployment/
# Run setup
python setup.py

# Or start services
python start.py
```

### Option 2: Use Full Path

```bash
# From any directory
cd "d:\sha projects\rakez\rakez-lead-scoring-deployment"
python setup.py
```

### Option 3: Use START_HERE.bat (Windows)

Double-click `START_HERE.bat` in the root directory for a menu-driven interface.

## 🎯 Correct Usage

### From Root Directory:

```bash
# Make sure you're here:
# d:\sha projects\rakez\rakez-lead-scoring-deployment\

# Setup (first time)
python setup.py

# Start all services
python start.py

# Start API only
python start.py --api-only

# Start Dashboard only
python start.py --dashboard-only
```

## 📁 Directory Structure

```
rakez-lead-scoring-deployment/          ← YOU NEED TO BE HERE
├── setup.py                            ← Setup script
├── start.py                            ← Start script
├── START_HERE.bat                      ← Windows launcher
│
├── 03_api/
│   ├── start_api.bat                  ← Helper (runs from root)
│   └── fastapi_app.py
│
└── 05_dashboard/
    ├── start_dashboard.bat            ← Helper (runs from root)
    └── streamlit_dashboard.py
```

## 🔧 Quick Commands from Anywhere

### Windows (PowerShell):
```powershell
cd "d:\sha projects\rakez\rakez-lead-scoring-deployment"
python setup.py
python start.py
```

### Windows (Command Prompt):
```cmd
cd "d:\sha projects\rakez\rakez-lead-scoring-deployment"
python setup.py
python start.py
```

## ✅ Verification

To check if you're in the right directory:

```bash
# Should show: setup.py, start.py, requirements.txt
dir

# Or
ls
```

If you see `setup.py` and `start.py` in the listing, you're in the right place!

---

**Remember: Always run `setup.py` and `start.py` from the root directory!** 🎯

