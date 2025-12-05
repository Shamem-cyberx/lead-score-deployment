# 🧹 File Cleanup and Organization Plan

## Files to Remove

### 1. Python Cache Files (__pycache__)
- All `__pycache__` directories - can be regenerated

### 2. Duplicate Test Files (03_api/)
**Keep:** `test_while_running.py` (most complete)
**Remove:**
- `test_explain_simple.py` (duplicate)
- `test_explain_endpoint.py` (duplicate)
- `test_backend.py` (if redundant with test_api_endpoints.py)

### 3. Duplicate Startup Scripts (03_api/)
**Keep:** `start_server.bat` (simplest, most direct)
**Remove:**
- `start_api.bat` (duplicate)
- `start_backend_simple.bat` (duplicate)
- `restart_backend.bat` (can use start_server.bat)
- `start_api.sh` (keep if needed for Linux)

### 4. Redundant Documentation (03_api/)
**Keep:**
- `SETUP_GUIDE.md` (main setup guide)
- `TEST_INSTRUCTIONS.md` (comprehensive testing guide)
**Remove:**
- `QUICK_TEST.md` (redundant)
- `RESTART_AND_TEST.md` (covered in TEST_INSTRUCTIONS.md)
- `START_BACKEND.md` (covered in SETUP_GUIDE.md)
- `SUMMARY.md` (redundant)
- `TEST_RESULTS.md` (temporary)
- `TEST_EXPLAIN_ENDPOINT.md` (covered in TEST_INSTRUCTIONS.md)
- `FIX_EXPLAINABILITY_ERROR.md` (temporary fix doc)

### 5. Dashboard - Duplicate Scripts (05_dashboard/)
**Keep:** `start_dash.bat`, `start_dash.sh`, `start_dash.ps1`
**Remove:**
- `start_dashboard.bat` (duplicate)
- `start_dashboard.sh` (duplicate)
- `start_backend.bat` (should be in 03_api/)
- `start_backend.ps1` (should be in 03_api/)

### 6. Dashboard - Redundant Documentation (05_dashboard/)
**Keep:**
- `README_DASH.md` (main dashboard guide)
- `EXPLAINABILITY_TAB.md` (feature-specific)
- `QUICK_START_DASH.md` (quick reference)
**Remove:**
- `DASHBOARD_COMPARISON.md` (historical)
- `DASHBOARD_UPGRADE.md` (historical)
- `DATA_LOADING_FIXED.md` (temporary fix)
- `DATA_VERIFICATION.md` (temporary)
- `FIXES_APPLIED.md` (temporary)
- `METRICS_UPDATE_SUMMARY.md` (temporary)
- `ONE_YEAR_DATA_README.md` (covered in README_DASH.md)
- `QUICK_COMMANDS.md` (covered in QUICK_START_DASH.md)
- `STANDALONE_DASHBOARD.md` (covered in README_DASH.md)
- `START_DASHBOARD.md` (covered in QUICK_START_DASH.md)
- `START_SERVICES.md` (covered in README_DASH.md)
- `TIME_RANGE_FIX_SUMMARY.md` (temporary)
- `TIME_RANGE_FIX.md` (temporary)
- `TIME_RANGE_FIXED.md` (temporary)
- `TIME_RANGE_TROUBLESHOOTING.md` (temporary)
- `TROUBLESHOOTING.md` (covered in README_DASH.md)
- `ADVANCED_METRICS.md` (covered in README_DASH.md)
- `OLLAMA_SETUP.md` (covered in README_DASH.md)
- `OLLAMA_TEST_RESULTS.md` (temporary)

### 7. Obsolete Files
**Remove:**
- `05_dashboard/streamlit_dashboard.py` (replaced by dash_dashboard.py)
- `05_dashboard/test_dashboard.py` (if not essential)
- `05_dashboard/test_ollama.py` (if not essential)
- `05_dashboard/test_time_range.py` (temporary test)
- `05_dashboard/update_sample_dates.py` (one-time script)
- `03_api/verify_model.py` (if redundant)

### 8. Root Level - Redundant Documentation
**Keep:**
- `README.md` (main readme)
- `START_HERE.md` (entry point)
- `INDEX.md` (navigation)
- `requirements.txt` (dependencies)
- `setup.py` (setup script)
- `start.py` (main startup)
**Review/Consolidate:**
- Multiple completion/verification reports
- Multiple quick start guides

## Files to Keep (Essential)

### Core Code
- All `.py` files in `02_notebooks/` (core functionality)
- `03_api/fastapi_app.py` (main API)
- `03_api/audit_logging.py` (audit system)
- `03_api/create_dummy_model.py` (model creation)
- `05_dashboard/dash_dashboard.py` (main dashboard)
- `05_dashboard/ollama_integration.py` (AI features)
- `05_dashboard/generate_one_year_data.py` (data generation)

### Configuration
- `requirements.txt`
- `setup.py`
- `04_ci_cd/github_actions.yaml`

### Documentation (Essential)
- `README.md`
- `START_HERE.md`
- `INDEX.md`
- `06_docs/presentation_slides.md`
- `06_docs/detailed_readme.md`
- `09_disaster_recovery/DISASTER_RECOVERY_PLAN.md`
- `10_governance/GOVERNANCE_FRAMEWORK.md`

### Data
- All files in `05_dashboard/sample_data/`
- `03_api/mlruns/` (MLflow model registry - KEEP!)

### Scripts (Essential)
- `START_HERE.bat`
- `start.py`
- `03_api/start_server.bat`
- `05_dashboard/start_dash.bat`, `.sh`, `.ps1`

