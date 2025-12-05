# 📁 Project Structure - RAKEZ Lead Scoring Model

## 🗂️ Directory Organization

```
rakez-lead-scoring-deployment/
│
├── 📄 README.md                    # Main project readme
├── 📄 START_HERE.md                # Quick start guide
├── 📄 INDEX.md                     # Navigation index
├── 📄 requirements.txt             # Python dependencies
├── 📄 setup.py                     # Setup script
├── 📄 start.py                     # Main startup script
├── 📄 START_HERE.bat               # Windows quick start
│
├── 📁 01_architecture/              # Architecture diagrams
│   ├── deployment_architecture.md
│   ├── monitoring_architecture.md
│   └── retraining_architecture.md
│
├── 📁 02_notebooks/                 # Core ML functionality
│   ├── drift_detection.py
│   ├── fairness_metrics.py
│   ├── model_explainability.py
│   ├── model_inference_databricks.py
│   ├── monitoring_metrics.py
│   └── retraining_pipeline.py
│
├── 📁 03_api/                       # FastAPI Backend
│   ├── fastapi_app.py              # Main API application
│   ├── audit_logging.py            # Audit logging system
│   ├── create_dummy_model.py       # Model creation script
│   ├── start_server.bat            # Windows startup
│   ├── start_api.sh                # Linux/Mac startup
│   ├── test_while_running.py       # Comprehensive test
│   ├── test_api_endpoints.py       # API endpoint tests
│   ├── verify_model.py             # Model verification
│   ├── SETUP_GUIDE.md              # Setup instructions
│   ├── TEST_INSTRUCTIONS.md        # Testing guide
│   └── mlruns/                     # MLflow model registry (KEEP!)
│
├── 📁 04_ci_cd/                     # CI/CD Pipeline
│   └── github_actions.yaml
│
├── 📁 05_dashboard/                 # Plotly Dash Dashboard
│   ├── dash_dashboard.py           # Main dashboard
│   ├── ollama_integration.py       # AI integration
│   ├── generate_one_year_data.py  # Data generation
│   ├── start_dash.bat              # Windows startup
│   ├── start_dash.sh               # Linux/Mac startup
│   ├── start_dash.ps1              # PowerShell startup
│   ├── test_dashboard.py           # Dashboard tests
│   ├── test_ollama.py              # Ollama tests
│   ├── README_DASH.md              # Dashboard guide
│   ├── QUICK_START_DASH.md         # Quick start
│   ├── EXPLAINABILITY_TAB.md       # Explainability guide
│   └── sample_data/                # Sample CSV data
│       ├── drift_detection.csv
│       ├── lead_conversions.csv
│       ├── leads_predictions.csv
│       └── monitoring_metrics.csv
│
├── 📁 06_docs/                      # Documentation
│   ├── presentation_slides.md      # 10-slide presentation
│   └── detailed_readme.md          # Detailed documentation
│
├── 📁 09_disaster_recovery/         # Disaster Recovery
│   └── DISASTER_RECOVERY_PLAN.md
│
└── 📁 10_governance/                # ML Governance
    ├── GOVERNANCE_FRAMEWORK.md
    └── model_approval.py
```

## 📋 Key Files

### 🚀 Getting Started
- **START_HERE.md** - Start here for first-time setup
- **README.md** - Main project documentation
- **INDEX.md** - Navigation guide

### 🔧 Setup & Configuration
- **requirements.txt** - Python dependencies
- **setup.py** - Automated setup script
- **start.py** - Main startup script

### 🎯 Core Components
- **03_api/fastapi_app.py** - FastAPI REST API
- **05_dashboard/dash_dashboard.py** - Monitoring dashboard
- **02_notebooks/** - ML pipelines and notebooks

### 📚 Documentation
- **06_docs/presentation_slides.md** - Assessment presentation
- **06_docs/detailed_readme.md** - Detailed documentation
- **SUBMISSION_PACKAGE.md** - Submission guide

### 🧪 Testing
- **03_api/test_while_running.py** - Comprehensive API test
- **03_api/test_api_endpoints.py** - API endpoint tests
- **05_dashboard/test_dashboard.py** - Dashboard tests

### 🚀 Startup Scripts
- **START_HERE.bat** - Windows quick start
- **03_api/start_server.bat** - Start API (Windows)
- **05_dashboard/start_dash.bat** - Start dashboard (Windows)

## 🗑️ Cleaned Up

The following have been removed:
- ✅ All `__pycache__` directories
- ✅ Duplicate test files
- ✅ Duplicate startup scripts
- ✅ Redundant documentation
- ✅ Obsolete files (streamlit_dashboard.py)
- ✅ Temporary fix documentation

See **CLEANUP_SUMMARY.md** for details.

## 📊 File Count

- **Core Python files:** ~15
- **Documentation files:** ~20 (essential only)
- **Test files:** 5 (essential)
- **Startup scripts:** 6 (one per platform)
- **Sample data files:** 4 CSV files

## ✅ Project Status

- ✅ Clean and organized
- ✅ No duplicate files
- ✅ Essential documentation consolidated
- ✅ All core functionality preserved
- ✅ Ready for submission

