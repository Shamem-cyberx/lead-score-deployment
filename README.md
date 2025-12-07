# RAKEZ Lead Scoring Model - Deployment & Monitoring

Complete end-to-end ML engineering solution for deploying and monitoring a lead scoring model.

## 🚀 Quick Start

```bash
# 1. Setup (one-time)
python setup.py

# 2. Start all services
python start.py

# 3. Access services
# - API Docs: http://localhost:8000/docs
# - Dashboard: http://localhost:8501
```

**See `QUICK_START.md` for detailed instructions.**

## 📋 Key Documents

- **🚀 Quick Start**: `QUICK_START.md` - Get started in 5 minutes
- **📦 Submission Package**: `SUBMISSION_PACKAGE.md` - Complete assessment overview
- **📄 Case Study**: `RAKEZ_CASE_STUDY_FINAL.md` - Full case study document (PDF-ready)
- **✅ Assessment Status**: `ASSESSMENT_COMPLETION.md` - Requirements checklist
- **📊 Presentation**: `06_docs/presentation_slides.md` - 10-slide presentation

## 📁 Project Structure

```
rakez-lead-scoring-deployment/
│
├── 01_architecture/
│   ├── deployment_architecture.md      # Deployment architecture diagram & docs
│   ├── monitoring_architecture.md     # Monitoring architecture diagram & docs
│   └── retraining_architecture.md      # Retraining architecture diagram & docs
│
├── 02_notebooks/
│   ├── model_inference_databricks.py  # Batch inference job
│   ├── drift_detection.py             # Drift detection monitoring
│   ├── monitoring_metrics.py          # Performance metrics tracking
│   └── retraining_pipeline.py         # Automated retraining workflow
│
├── 03_api/
│   └── fastapi_app.py                 # Real-time scoring API with shadow model
│
├── 04_ci_cd/
│   └── github_actions.yaml            # CI/CD pipeline configuration
│
├── 05_dashboard/
│   └── streamlit_dashboard.py         # Monitoring dashboard
│
├── 06_docs/
│   ├── detailed_readme.md             # Comprehensive documentation
│   ├── presentation_slides.md         # 10-slide presentation content
│   ├── ARCHITECTURE_DIAGRAMS.md       # All architecture diagrams (9 diagrams)
│   ├── DIAGRAM_INDEX.md               # Diagram navigation guide
│   ├── RAKEZ_case_study_slides.pdf   # PDF version (to be generated)
│   └── RAKEZ_case_study_slides.pptx  # PPT version (to be generated)
│
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="your-token"
   export MLFLOW_TRACKING_URI="your-mlflow-uri"
   ```

3. **Deploy to Databricks**
   ```bash
   databricks workspace import_dir 02_notebooks /Workspace/lead_scoring/notebooks
   ```

4. **Start API Server**
   ```bash
   cd 03_api
   uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
   ```

5. **Start Dashboard**
   ```bash
   cd 05_dashboard
   streamlit run streamlit_dashboard.py
   ```

## 📚 Documentation

- **Detailed README**: See `06_docs/detailed_readme.md` for comprehensive documentation
- **All Architecture Diagrams**: See `06_docs/ARCHITECTURE_DIAGRAMS.md` for complete collection (9 diagrams)
- **Diagram Index**: See `06_docs/DIAGRAM_INDEX.md` for quick navigation
- **Detailed Architecture**: See `01_architecture/` for technical documentation with diagrams
- **Presentation**: See `06_docs/presentation_slides.md` for 10-slide presentation

## 🎯 Key Features

- ✅ Production-ready Databricks notebooks
- ✅ MLflow model registry integration
- ✅ Real-time FastAPI inference endpoint
- ✅ Shadow model deployment
- ✅ Comprehensive drift detection (PSI, KL Divergence)
- ✅ Automated retraining pipeline
- ✅ CI/CD with GitHub Actions
- ✅ Streamlit monitoring dashboard
- ✅ Complete documentation

## 📊 Architecture Highlights

- **Data Sources**: CRM (PostgreSQL), Web Forms
- **Processing**: Databricks + Delta Lake
- **Model Registry**: MLflow (Production/Staging/Archived)
- **API**: FastAPI with shadow model support
- **Monitoring**: Streamlit dashboard + automated alerts
- **CI/CD**: GitHub Actions with canary deployment

## 🔧 Technologies

- **ML**: XGBoost, LightGBM, scikit-learn
- **Platform**: Databricks, MLflow
- **API**: FastAPI, Uvicorn
- **Dashboard**: Streamlit, Plotly
- **CI/CD**: GitHub Actions
- **Data**: Delta Lake, Spark

## 📝 Notes

- All code is production-ready and tested
- Architecture diagrams use Mermaid format (render in Markdown viewers)
- Presentation slides are in Markdown format (convert to PPT/PDF as needed)
- No Docker required - Databricks-native execution

## 📧 Support

For questions or issues, contact the ML Engineering team.

---

**RAKEZ Lead Scoring Model - Production Deployment System**

