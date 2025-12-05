# RAKEZ Lead Scoring Model - Deployment & Monitoring

## Executive Summary

This project implements a complete end-to-end ML engineering solution for deploying and monitoring a lead scoring model for RAKEZ. The system includes production-ready code for Databricks, real-time API serving, comprehensive monitoring, automated drift detection, and CI/CD pipelines.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Model Deployment](#model-deployment)
4. [Monitoring & Alerting](#monitoring--alerting)
5. [Drift Detection](#drift-detection)
6. [Retraining Strategy](#retraining-strategy)
7. [REST API Design](#rest-api-design)
8. [CRM Integration Plan](#crm-integration-plan)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Getting Started](#getting-started)

---

## Project Overview

### Problem Statement

RAKEZ needs a production-ready lead scoring system that:
- Scores leads in real-time to prioritize sales efforts
- Monitors model performance and data quality continuously
- Detects and responds to data drift automatically
- Retrains models when performance degrades
- Integrates seamlessly with existing CRM systems

### Solution

A comprehensive ML engineering platform built on:
- **Databricks**: Data processing, feature engineering, and batch inference
- **MLflow**: Model versioning and registry
- **FastAPI**: Real-time scoring API
- **Streamlit**: Monitoring dashboard
- **GitHub Actions**: CI/CD automation

---

## Architecture

### High-Level Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   CRM/DB   │────▶│  Delta Lake  │────▶│ Databricks  │
│ PostgreSQL  │     │ Bronze/Silver│     │  Workspace  │
└─────────────┘     └──────────────┘     └─────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ MLflow Registry │
                                    │  (Production)   │
                                    └─────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    │                                                     │
                    ▼                                                     ▼
            ┌──────────────┐                                  ┌──────────────┐
            │  FastAPI API  │                                  │  Batch Jobs   │
            │  Real-time    │                                  │  Scheduled    │
            └──────────────┘                                  └──────────────┘
                    │                                                     │
                    ▼                                                     ▼
            ┌──────────────┐                                  ┌──────────────┐
            │   Monitoring │                                  │   Drift      │
            │   Dashboard  │                                  │  Detection   │
            └──────────────┘                                  └──────────────┘
```

### Component Details

1. **Data Sources**
   - CRM System (PostgreSQL): Lead information, contact details, interaction history
   - Web Forms/API: Real-time lead submissions

2. **Databricks Workspace**
   - Delta Lake: Medallion architecture (Bronze → Silver → Gold)
   - MLflow Model Registry: Production, Staging, Archived models
   - Databricks Jobs: Scheduled batch inference and monitoring

3. **API Layer**
   - FastAPI Service: RESTful API for real-time scoring
   - Shadow Model: Parallel evaluation of new models

4. **Monitoring System**
   - Drift Detection: PSI, KL Divergence, statistical tests
   - Performance Metrics: Latency, throughput, conversion rates
   - Alerting: Slack, Email, PagerDuty integration

5. **Visualization**
   - Streamlit Dashboard: Real-time monitoring
   - MLflow UI: Experiment tracking

---

## Model Deployment

### Deployment Strategy

1. **Model Registry (MLflow)**
   - Production: Current live model
   - Staging: Candidate models for promotion
   - Archived: Previous versions for rollback

2. **Deployment Methods**
   - **Batch Inference**: Scheduled Databricks jobs process historical leads
   - **Real-time Inference**: FastAPI endpoint serves on-demand requests
   - **Shadow Deployment**: New models evaluated in parallel without affecting production

3. **Canary Deployment**
   - Phase 1: 10% traffic (1 day)
   - Phase 2: 50% traffic (2 days)
   - Phase 3: 100% traffic
   - Automatic rollback on failure

### Deployment Steps

1. **Register Model to MLflow**
   ```python
   mlflow.register_model(model_uri, "lead_scoring_model")
   ```

2. **Transition to Staging**
   ```python
   client.transition_model_version_stage(
       name="lead_scoring_model",
       version=2,
       stage="Staging"
   )
   ```

3. **Shadow Testing** (1-2 weeks)
   - Deploy shadow model alongside production
   - Compare predictions silently
   - Monitor performance metrics

4. **Promote to Production**
   - Manual approval after shadow testing
   - Canary deployment
   - Full rollout

---

## Monitoring & Alerting

### Key Metrics

1. **Latency Metrics**
   - P50, P95, P99 percentiles
   - Target: P95 < 200ms
   - Alert: P95 > 500ms (Critical)

2. **Throughput**
   - Requests per second
   - Target: > 10 req/s
   - Alert: < 10 req/s (Warning)

3. **Error Rate**
   - HTTP error percentage
   - Target: < 1%
   - Alert: > 1% (Critical)

4. **Business Metrics**
   - Conversion rate (leads → customers)
   - Revenue per lead
   - Score distribution

### Alerting System

- **Level 1 (Info)**: Logged to dashboard
- **Level 2 (Warning)**: Slack notification to #ml-alerts
- **Level 3 (Critical)**: Email + Slack + PagerDuty

### Monitoring Schedule

- **Real-time**: API latency, throughput, error rates
- **Hourly**: Feature statistics, distribution checks
- **Daily**: PSI calculation, KL divergence, accuracy metrics
- **Weekly**: Comprehensive drift report

---

## Drift Detection

### Drift Types

1. **Data Drift**
   - Changes in feature distributions
   - New categories in categorical features
   - Missing value patterns

2. **Concept Drift**
   - Changes in relationship between features and target
   - Model performance degradation

### Detection Methods

1. **PSI (Population Stability Index)**
   - Threshold: PSI > 0.25 (Warning), PSI > 0.5 (Critical)
   - Calculated per feature and overall

2. **KL Divergence**
   - Measures distribution shift
   - Threshold: KL > 0.1

3. **Statistical Tests**
   - Kolmogorov-Smirnov test (continuous features)
   - Chi-square test (categorical features)
   - P-value threshold: < 0.05

### Drift Response

- **Warning (PSI 0.25-0.5)**: Monitor closely, prepare for retraining
- **Critical (PSI > 0.5)**: Trigger automatic retraining pipeline

---

## Retraining Strategy

### Retraining Triggers

1. **Drift-Triggered**: Automatic when PSI > 0.25 or significant distribution shift
2. **Scheduled**: Weekly for first 3 months, then monthly
3. **Manual**: Admin-initiated for special cases

### Retraining Workflow

1. **Data Collection**
   - Latest 6 months of labeled data
   - Minimum 10,000 records required

2. **Model Training**
   - Hyperparameter optimization (Optuna, 50-100 trials)
   - Time series cross-validation
   - XGBoost/LightGBM models

3. **Model Evaluation**
   - Must outperform current production model
   - Minimum improvement: +2% AUC or +5% business KPI
   - Shadow testing for 1-2 weeks

4. **Model Promotion**
   - Register to MLflow Staging
   - Manual review and approval
   - Canary deployment
   - Promote to Production

### Rollback Mechanism

- Automatic rollback triggers:
  - Error rate > 2%
  - Latency degradation > 50%
  - Business KPI drop > 10%
- One-click manual rollback to previous version

---

## REST API Design

### Endpoints

#### 1. Health Check
```
GET /health
Response: {
  "status": "healthy",
  "model_loaded": true,
  "model_stage": "Production",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### 2. Score Lead
```
POST /score-lead
Request: {
  "lead_id": "lead_123",
  "company_size": "Medium",
  "industry": "Technology",
  "page_views": 15,
  "time_on_site": 300.5,
  "form_completion_time": 45.2,
  "referral_source": "Google",
  "created_at": "2024-01-01T00:00:00"
}
Response: {
  "lead_id": "lead_123",
  "lead_score": 0.75,
  "score_category": "High",
  "model_version": "production_v1.0",
  "prediction_timestamp": "2024-01-01T00:00:01",
  "latency_ms": 45.2
}
```

#### 3. Model Info
```
GET /model-info
Response: {
  "production_model": {
    "loaded": true,
    "stage": "Production"
  },
  "shadow_model": {
    "enabled": true,
    "loaded": true,
    "stage": "Staging"
  }
}
```

### API Features

- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Comprehensive error messages
- **Request Logging**: All requests logged for monitoring
- **Shadow Model**: Parallel evaluation without affecting response
- **CORS Support**: Configurable CORS middleware

---

## CRM Integration Plan

### Integration Architecture

```
FastAPI API → Webhook/API → CRM System (PostgreSQL)
              ↓
         Delta Table (CRM Updates)
```

### Integration Methods

1. **Webhook Integration**
   - FastAPI sends webhook on each prediction
   - CRM system receives lead score via webhook
   - Updates lead record in CRM database

2. **API Integration**
   - CRM system calls FastAPI endpoint
   - Real-time scoring on demand
   - Batch updates via scheduled jobs

3. **Database Integration**
   - Delta table with lead scores
   - CRM system queries Delta table periodically
   - Sync mechanism ensures consistency

### Data Flow

1. Lead created in CRM → Stored in Delta Lake
2. Batch job scores leads → Updates Delta table
3. CRM queries Delta table → Updates lead records
4. Sales team sees scores in CRM interface

### Implementation Steps

1. **Phase 1**: Batch integration (Delta table)
   - Scheduled job updates CRM scores daily
   - Low latency requirement

2. **Phase 2**: Real-time integration (Webhook)
   - FastAPI sends webhook on prediction
   - CRM receives score immediately
   - Higher latency requirement

3. **Phase 3**: API integration
   - CRM calls FastAPI directly
   - On-demand scoring
   - Highest latency requirement

---

## CI/CD Pipeline

### Pipeline Stages

1. **Lint and Test**
   - Code formatting (Black)
   - Linting (Flake8)
   - Unit tests (Pytest)

2. **Validate Notebooks**
   - Syntax validation
   - Import checks

3. **Deploy to Staging**
   - Deploy notebooks to Databricks
   - Create/update Databricks jobs
   - Trigger inference job

4. **Deploy to Production**
   - Validate MLflow model
   - Deploy notebooks
   - Canary deployment (10% → 50% → 100%)
   - Monitor metrics
   - Rollback on failure

5. **Model Registry Update**
   - Promote model from Staging to Production
   - Update model tags and metadata

### GitHub Actions Workflow

See `04_ci_cd/github_actions.yaml` for complete workflow definition.

### Deployment Secrets

Required GitHub Secrets:
- `DATABRICKS_HOST`: Databricks workspace URL
- `DATABRICKS_TOKEN`: Databricks access token
- `MLFLOW_TRACKING_URI`: MLflow tracking server URI
- `DATABRICKS_JOB_ID_INFERENCE`: Inference job ID

---

## Getting Started

### Prerequisites

- Databricks workspace
- MLflow tracking server
- Python 3.9+
- Access to Delta Lake tables

### Installation

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd rakez-lead-scoring-deployment
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="your-token"
   export MLFLOW_TRACKING_URI="your-mlflow-uri"
   ```

4. **Deploy Notebooks to Databricks**
   ```bash
   databricks workspace import_dir 02_notebooks /Workspace/lead_scoring/notebooks
   ```

5. **Start FastAPI Server**
   ```bash
   cd 03_api
   uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
   ```

6. **Start Streamlit Dashboard**
   ```bash
   cd 05_dashboard
   streamlit run streamlit_dashboard.py
   ```

### Running Jobs

1. **Batch Inference**
   - Create Databricks job from `model_inference_databricks.py`
   - Schedule: Daily at 2 AM

2. **Drift Detection**
   - Create Databricks job from `drift_detection.py`
   - Schedule: Daily at 6 AM

3. **Monitoring Metrics**
   - Create Databricks job from `monitoring_metrics.py`
   - Schedule: Hourly

4. **Retraining Pipeline**
   - Create Databricks job from `retraining_pipeline.py`
   - Schedule: Weekly or trigger on drift

---

## Troubleshooting

### Common Issues

1. **Model Not Loading**
   - Check MLflow tracking URI
   - Verify model exists in registry
   - Check model stage (Production/Staging)

2. **High Latency**
   - Check feature engineering performance
   - Optimize model inference
   - Scale API server

3. **Drift Alerts**
   - Review feature distributions
   - Check data quality
   - Trigger retraining if needed

4. **API Errors**
   - Check input validation
   - Review error logs
   - Verify model is loaded

---

## Support & Contact

For questions or issues, please contact the ML Engineering team.

---

## License

Proprietary - RAKEZ Internal Use Only

