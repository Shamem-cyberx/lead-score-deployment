# Retraining Architecture

## Overview
Automated model retraining pipeline triggered by drift detection or scheduled intervals.

## Mermaid Diagram

```mermaid
graph TB
    subgraph "Trigger Sources"
        DRIFT[Drift Detection<br/>PSI > Threshold]
        SCHEDULE[Scheduled Trigger<br/>Weekly/Monthly]
        MANUAL[Manual Trigger<br/>Admin Panel]
    end
    
    subgraph "Data Preparation"
        DATA_COLLECT[Data Collection<br/>Delta Lake]
        FEAT_ENG[Feature Engineering<br/>Notebook]
        TRAIN_TEST[Train/Test Split<br/>Time-based]
        VALIDATION[Validation Set<br/>Holdout]
    end
    
    subgraph "Model Training"
        MLFLOW_EXP[MLflow Experiment<br/>Tracking]
        HYPEROPT[Hyperparameter Tuning<br/>Optuna/Bayesian]
        CROSS_VAL[Cross-Validation<br/>Time Series Split]
        MODEL_TRAIN[Model Training<br/>XGBoost/LightGBM]
    end
    
    subgraph "Model Evaluation"
        METRICS[Performance Metrics<br/>AUC, Precision, Recall]
        BASELINE_COMP[Baseline Comparison<br/>Current Production]
        SHADOW_TEST[Shadow Testing<br/>Parallel Evaluation]
        BUSINESS_KPI[Business KPIs<br/>Conversion Rate, Revenue]
    end
    
    subgraph "Model Registry"
        STAGING[Staging Registry<br/>Candidate Models]
        PROD[Production Registry<br/>Live Model]
        ARCHIVE[Archive Registry<br/>Previous Versions]
    end
    
    subgraph "Deployment Pipeline"
        CI_CD[CI/CD Pipeline<br/>GitHub Actions]
        APPROVAL[Approval Gate<br/>Manual Review]
        CANARY[Canary Deployment<br/>10% → 50% → 100%]
        PROMOTE[Model Promotion<br/>Staging → Production]
    end
    
    subgraph "Rollback"
        ROLLBACK[Rollback Mechanism<br/>Previous Version]
        MONITOR[Post-Deployment<br/>Monitoring]
    end
    
    DRIFT --> DATA_COLLECT
    SCHEDULE --> DATA_COLLECT
    MANUAL --> DATA_COLLECT
    
    DATA_COLLECT --> FEAT_ENG
    FEAT_ENG --> TRAIN_TEST
    TRAIN_TEST --> VALIDATION
    
    VALIDATION --> MLFLOW_EXP
    MLFLOW_EXP --> HYPEROPT
    HYPEROPT --> CROSS_VAL
    CROSS_VAL --> MODEL_TRAIN
    
    MODEL_TRAIN --> METRICS
    METRICS --> BASELINE_COMP
    BASELINE_COMP --> SHADOW_TEST
    SHADOW_TEST --> BUSINESS_KPI
    
    BUSINESS_KPI --> STAGING
    STAGING --> CI_CD
    CI_CD --> APPROVAL
    APPROVAL --> CANARY
    CANARY --> PROMOTE
    PROMOTE --> PROD
    
    PROD --> MONITOR
    MONITOR --> ROLLBACK
    ROLLBACK --> ARCHIVE
    
    style DRIFT fill:#FF5722
    style MLFLOW_EXP fill:#4CAF50
    style STAGING fill:#FF9800
    style PROD fill:#2196F3
    style ROLLBACK fill:#F44336
```

## Retraining Workflow

### 1. Trigger Sources
- **Drift Detection**: Automatic trigger when PSI > 0.25 or significant distribution shift detected
- **Scheduled Trigger**: Weekly or monthly retraining regardless of drift
- **Manual Trigger**: Admin-initiated retraining for special cases

### 2. Data Preparation
- **Data Collection**: 
  - Latest 6 months of labeled data from Delta Lake
  - Ensures sufficient sample size (minimum 10,000 records)
- **Feature Engineering**: 
  - Reapplies same transformations as production
  - Handles missing values, encoding, scaling
- **Train/Test Split**: 
  - Time-based split (80/20)
  - Prevents data leakage
- **Validation Set**: 
  - Holdout set for final evaluation
  - Represents most recent data

### 3. Model Training
- **MLflow Experiment Tracking**: 
  - Logs all hyperparameters, metrics, artifacts
  - Enables experiment comparison
- **Hyperparameter Tuning**: 
  - Optuna or Bayesian optimization
  - 50-100 trials per experiment
- **Cross-Validation**: 
  - Time series cross-validation
  - Respects temporal ordering
- **Model Training**: 
  - XGBoost or LightGBM
  - Early stopping to prevent overfitting

### 4. Model Evaluation
- **Performance Metrics**: 
  - AUC-ROC (primary metric)
  - Precision, Recall, F1-score
  - Calibration metrics (Brier score)
- **Baseline Comparison**: 
  - Must outperform current production model
  - Minimum improvement: +2% AUC or +5% business KPI
- **Shadow Testing**: 
  - Deploy to shadow mode for 1-2 weeks
  - Compare predictions with production
- **Business KPIs**: 
  - Conversion rate improvement
  - Revenue per lead increase
  - Sales team feedback

### 5. Model Registry
- **Staging Registry**: 
  - Candidate models awaiting approval
  - Tagged with experiment ID and metrics
- **Production Registry**: 
  - Current live model
  - Only one production model at a time
- **Archive Registry**: 
  - Previous model versions
  - Maintained for rollback capability

### 6. Deployment Pipeline
- **CI/CD Pipeline**: 
  - Automated testing (unit, integration)
  - Model validation checks
  - Databricks job deployment
- **Approval Gate**: 
  - Manual review by ML lead
  - Business stakeholder sign-off
- **Canary Deployment**: 
  - Phase 1: 10% traffic (1 day)
  - Phase 2: 50% traffic (2 days)
  - Phase 3: 100% traffic
- **Model Promotion**: 
  - Automatic promotion after successful canary
  - Updates MLflow registry tags

### 7. Rollback Mechanism
- **Automatic Rollback Triggers**: 
  - Error rate > 2%
  - Latency degradation > 50%
  - Business KPI drop > 10%
- **Manual Rollback**: 
  - One-click rollback to previous version
  - Maintains model registry history
- **Post-Deployment Monitoring**: 
  - Intensive monitoring for 48 hours
  - Daily performance reports

## Retraining Schedule

- **Drift-Triggered**: As needed (typically monthly)
- **Scheduled**: Weekly for first 3 months, then monthly
- **Emergency**: Manual trigger for critical issues

## Model Versioning

- **Version Format**: `v{MAJOR}.{MINOR}.{PATCH}`
  - MAJOR: Breaking changes, new features
  - MINOR: Performance improvements
  - PATCH: Bug fixes, minor updates
- **Metadata Stored**: 
  - Training date, data range, metrics
  - Feature list, hyperparameters
  - Model artifacts, dependencies

