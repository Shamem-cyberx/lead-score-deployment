# 🎨 RAKEZ Lead Scoring - Complete Architecture Diagrams

This document contains all visual architecture diagrams for the RAKEZ Lead Scoring Model deployment and monitoring system.

---

## 📑 Table of Contents

1. [System Overview](#1-system-overview)
2. [Deployment Architecture](#2-deployment-architecture)
3. [Monitoring Architecture](#3-monitoring-architecture)
4. [Retraining Architecture](#4-retraining-architecture)
5. [API Request Flow (Sequence)](#5-api-request-flow-sequence)
6. [Data Flow (Medallion Architecture)](#6-data-flow-medallion-architecture)
7. [CI/CD Pipeline](#7-cicd-pipeline)
8. [Model Lifecycle](#8-model-lifecycle)
9. [Component Interaction](#9-component-interaction)

---

## 1. System Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        CRM[CRM System<br/>PostgreSQL]
        WEB[Web Forms<br/>API]
        HIST[Historical Data<br/>CSV/Delta]
    end
    
    subgraph "Data Processing Layer"
        DELTA[Delta Lake<br/>Bronze/Silver/Gold]
        FEAT[Feature Engineering<br/>Databricks]
    end
    
    subgraph "Model Management"
        MLFLOW[MLflow Registry<br/>Production/Staging]
        TRAIN[Training Pipeline<br/>Automated]
    end
    
    subgraph "Serving Layer"
        API[FastAPI<br/>Real-time API]
        BATCH[Batch Jobs<br/>Scheduled]
        SHADOW[Shadow Model<br/>Evaluation]
    end
    
    subgraph "Monitoring & Operations"
        MONITOR[Monitoring Service<br/>Drift Detection]
        DASH[Dashboard<br/>Plotly Dash]
        ALERTS[Alerting<br/>Slack/Email]
    end
    
    subgraph "Downstream"
        CRM_OUT[CRM Integration<br/>Lead Scores]
        ANALYTICS[Analytics<br/>Business Metrics]
    end
    
    CRM --> DELTA
    WEB --> DELTA
    HIST --> DELTA
    DELTA --> FEAT
    FEAT --> TRAIN
    TRAIN --> MLFLOW
    MLFLOW --> API
    MLFLOW --> BATCH
    MLFLOW --> SHADOW
    API --> MONITOR
    BATCH --> MONITOR
    SHADOW --> MONITOR
    MONITOR --> DASH
    MONITOR --> ALERTS
    API --> CRM_OUT
    BATCH --> CRM_OUT
    MONITOR --> ANALYTICS
    
    style MLFLOW fill:#4CAF50
    style API fill:#2196F3
    style MONITOR fill:#FF9800
    style SHADOW fill:#9C27B0
    style DELTA fill:#00BCD4
```

---

## 2. Deployment Architecture

### Complete Deployment Flow

```mermaid
graph TB
    subgraph "Data Sources"
        CRM[CRM System<br/>PostgreSQL]
        WEB[Web Forms<br/>API]
    end
    
    subgraph "Databricks Workspace"
        DB[Delta Lake<br/>Bronze/Silver/Gold]
        MLFLOW[MLflow Model Registry<br/>Production/Staging]
        JOB[Databricks Job<br/>Batch Inference]
    end
    
    subgraph "API Layer"
        FASTAPI[FastAPI Service<br/>/score-lead endpoint]
        SHADOW[Shadow Model<br/>Silent Evaluation]
    end
    
    subgraph "Monitoring"
        MONITOR[Monitoring Service<br/>Drift Detection]
        ALERTS[Alert System<br/>Slack/Email]
    end
    
    subgraph "Downstream Systems"
        CRM_OUT[CRM Integration<br/>Lead Scores]
        DASH[Streamlit Dashboard<br/>Real-time Metrics]
    end
    
    CRM --> DB
    WEB --> DB
    DB --> JOB
    MLFLOW --> JOB
    JOB --> FASTAPI
    MLFLOW --> FASTAPI
    FASTAPI --> SHADOW
    FASTAPI --> CRM_OUT
    JOB --> MONITOR
    FASTAPI --> MONITOR
    MONITOR --> ALERTS
    MONITOR --> DASH
    
    style MLFLOW fill:#4CAF50
    style FASTAPI fill:#2196F3
    style MONITOR fill:#FF9800
    style SHADOW fill:#9C27B0
```

**Key Components:**
- **MLflow Registry**: Manages model versions (Production, Staging, Archived)
- **FastAPI**: Real-time scoring API with < 200ms latency target
- **Shadow Model**: Parallel evaluation without affecting production
- **Delta Lake**: Medallion architecture for data versioning

---

## 3. Monitoring Architecture

### Comprehensive Monitoring System

```mermaid
graph TB
    subgraph "Data Collection"
        API_LOGS[API Request Logs<br/>FastAPI]
        BATCH_LOGS[Batch Job Logs<br/>Databricks]
        PRED_LOGS[Prediction Logs<br/>Delta Table]
    end
    
    subgraph "Drift Detection"
        PSI[PSI Calculator<br/>Population Stability Index]
        KL[KL Divergence<br/>Feature Distribution]
        STATS[Statistical Tests<br/>KS Test, Chi-square]
    end
    
    subgraph "Performance Metrics"
        LATENCY[Latency Monitor<br/>P50, P95, P99]
        THROUGHPUT[Throughput Monitor<br/>Requests/sec]
        ACCURACY[Accuracy Metrics<br/>Conversion Rate]
    end
    
    subgraph "Feature Monitoring"
        FEAT_STATS[Feature Statistics<br/>Mean, Std, Missing]
        DIST_COMP[Distribution Comparison<br/>Baseline vs Current]
        OUTLIERS[Outlier Detection<br/>IQR, Z-score]
    end
    
    subgraph "Alerting System"
        RULES[Alert Rules Engine<br/>Thresholds]
        SLACK[Slack Notifications<br/>#ml-alerts]
        EMAIL[Email Alerts<br/>Team Distribution]
        PAGERDUTY[PagerDuty<br/>Critical Issues]
    end
    
    subgraph "Visualization"
        DASH[Plotly Dash Dashboard<br/>Real-time Charts]
        GRAFANA[Grafana Dashboards<br/>System Metrics]
        MLFLOW_UI[MLflow UI<br/>Experiment Tracking]
    end
    
    API_LOGS --> PRED_LOGS
    BATCH_LOGS --> PRED_LOGS
    PRED_LOGS --> PSI
    PRED_LOGS --> KL
    PRED_LOGS --> STATS
    PRED_LOGS --> FEAT_STATS
    PRED_LOGS --> DIST_COMP
    PRED_LOGS --> OUTLIERS
    
    API_LOGS --> LATENCY
    API_LOGS --> THROUGHPUT
    PRED_LOGS --> ACCURACY
    
    PSI --> RULES
    KL --> RULES
    STATS --> RULES
    FEAT_STATS --> RULES
    LATENCY --> RULES
    THROUGHPUT --> RULES
    ACCURACY --> RULES
    
    RULES --> SLACK
    RULES --> EMAIL
    RULES --> PAGERDUTY
    
    PRED_LOGS --> DASH
    LATENCY --> GRAFANA
    THROUGHPUT --> GRAFANA
    FEAT_STATS --> MLFLOW_UI
    
    style PSI fill:#FF5722
    style RULES fill:#F44336
    style DASH fill:#4CAF50
    style SLACK fill:#9C27B0
```

**Monitoring Schedule:**
- **Real-time**: API latency, throughput, error rates
- **Hourly**: Feature statistics, distribution checks
- **Daily**: PSI calculation, KL divergence, accuracy metrics
- **Weekly**: Comprehensive drift report

---

## 4. Retraining Architecture

### Automated Retraining Pipeline

```mermaid
graph TB
    subgraph "Trigger Sources"
        DRIFT[Drift Detection<br/>PSI > 0.25]
        SCHEDULE[Scheduled Trigger<br/>Weekly/Monthly]
        MANUAL[Manual Trigger<br/>Admin Panel]
        BUSINESS[Business Metrics<br/>Conversion Drop > 10%]
    end
    
    subgraph "Data Preparation"
        DATA_COLLECT[Data Collection<br/>Delta Lake - 6 months]
        FEAT_ENG[Feature Engineering<br/>Notebook]
        TRAIN_TEST[Train/Test Split<br/>Time-based 80/20]
        VALIDATION[Validation Set<br/>Holdout]
    end
    
    subgraph "Model Training"
        MLFLOW_EXP[MLflow Experiment<br/>Tracking]
        HYPEROPT[Hyperparameter Tuning<br/>Optuna - 50-100 trials]
        CROSS_VAL[Cross-Validation<br/>Time Series Split]
        MODEL_TRAIN[Model Training<br/>XGBoost/LightGBM]
    end
    
    subgraph "Model Evaluation"
        METRICS[Performance Metrics<br/>AUC, Precision, Recall]
        BASELINE_COMP[Baseline Comparison<br/>Current Production]
        SHADOW_TEST[Shadow Testing<br/>Parallel Evaluation 1-2 weeks]
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
        MONITOR[Post-Deployment<br/>Monitoring 48 hours]
    end
    
    DRIFT --> DATA_COLLECT
    SCHEDULE --> DATA_COLLECT
    MANUAL --> DATA_COLLECT
    BUSINESS --> DATA_COLLECT
    
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
    style BUSINESS fill:#FF5722
    style MLFLOW_EXP fill:#4CAF50
    style STAGING fill:#FF9800
    style PROD fill:#2196F3
    style ROLLBACK fill:#F44336
```

**Retraining Triggers:**
- **Drift-Triggered**: PSI > 0.25 or significant distribution shift
- **Scheduled**: Weekly (first 3 months), then monthly
- **Business Metrics**: Conversion rate drop > 10%
- **Manual**: Admin-initiated for special cases

---

## 5. API Request Flow (Sequence)

### Real-time Scoring Request Flow

```mermaid
sequenceDiagram
    participant Client as Client/CRM
    participant API as FastAPI Service
    participant MLflow as MLflow Registry
    participant Model as Production Model
    participant Shadow as Shadow Model
    participant Delta as Delta Lake
    participant Monitor as Monitoring Service
    participant Dashboard as Dashboard
    
    Client->>API: POST /score-lead<br/>{lead_data}
    API->>API: Validate Input<br/>(Pydantic)
    
    par Parallel Processing
        API->>MLflow: Load Production Model
        MLflow-->>API: Model Artifact
        API->>Model: Prepare Features<br/>(Encoding, Scaling)
        Model->>Model: Predict Score
        Model-->>API: Lead Score (0-1)
    and Shadow Evaluation
        API->>Shadow: Evaluate (if enabled)
        Shadow-->>API: Shadow Score
    end
    
    API->>Delta: Log Prediction<br/>(Timestamp, Features, Score)
    API->>Monitor: Update Metrics<br/>(Latency, Throughput)
    
    Monitor->>Dashboard: Real-time Update
    
    API-->>Client: Response<br/>{score, probability, timestamp}
    
    Note over Monitor,Dashboard: Drift Detection<br/>Runs Hourly/Daily
    Monitor->>Monitor: Calculate PSI<br/>Check Thresholds
    alt PSI > 0.25
        Monitor->>Monitor: Trigger Alert
        Monitor->>Monitor: Flag for Retraining
    end
```

**Key Features:**
- **Input Validation**: Pydantic models ensure data quality
- **Shadow Model**: Parallel evaluation without affecting production
- **Logging**: All predictions logged to Delta Lake for audit
- **Monitoring**: Real-time metrics update

---

## 6. Data Flow (Medallion Architecture)

### Delta Lake Medallion Architecture

```mermaid
flowchart LR
    subgraph "Data Sources"
        A1[CRM System]
        A2[Web Forms]
        A3[External APIs]
    end
    
    subgraph "Bronze Layer - Raw Data"
        B1[Raw Ingestion]
        B2[Schema Validation]
        B3[Timestamp Tracking]
    end
    
    subgraph "Silver Layer - Cleaned Data"
        C1[Data Cleaning]
        C2[Deduplication]
        C3[Type Conversion]
        C4[Null Handling]
    end
    
    subgraph "Gold Layer - Features"
        D1[Feature Engineering]
        D2[Aggregations]
        D3[Transformations]
        D4[Feature Store]
    end
    
    subgraph "Model Operations"
        E1[Training Data]
        E2[Inference Data]
        E3[Monitoring Data]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    
    B1 --> B2
    B2 --> B3
    B3 --> C1
    
    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> D1
    
    D1 --> D2
    D2 --> D3
    D3 --> D4
    
    D4 --> E1
    D4 --> E2
    D4 --> E3
    
    style B1 fill:#E3F2FD
    style C1 fill:#BBDEFB
    style D1 fill:#90CAF9
    style E1 fill:#64B5F6
```

**Data Quality Gates:**
- **Bronze**: Schema validation, timestamp tracking
- **Silver**: Data cleaning, deduplication, null handling
- **Gold**: Feature engineering, aggregations, transformations

---

## 7. CI/CD Pipeline

### Complete CI/CD Workflow

```mermaid
flowchart TD
    START([Code Push / PR]) --> LINT{Lint & Test}
    
    LINT -->|Fail| FAIL1[❌ Fail Build]
    LINT -->|Pass| VALIDATE{Validate Notebooks}
    
    VALIDATE -->|Fail| FAIL2[❌ Fail Build]
    VALIDATE -->|Pass| BRANCH{Branch?}
    
    BRANCH -->|develop| STAGING[Deploy to Staging]
    BRANCH -->|main| PROD_CHECK{Production<br/>Approval?}
    
    STAGING --> STAGING_TEST[Run Tests]
    STAGING_TEST --> STAGING_DEPLOY[Deploy to Databricks<br/>Staging]
    
    PROD_CHECK -->|Approved| PROD_DEPLOY[Deploy to Production]
    PROD_CHECK -->|Rejected| REJECT[❌ Deployment Blocked]
    
    PROD_DEPLOY --> VALIDATE_MODEL[Validate MLflow Model]
    VALIDATE_MODEL --> CANARY_10[Canary: 10% Traffic<br/>1 Day]
    
    CANARY_10 --> CHECK_10{Metrics OK?}
    CHECK_10 -->|No| ROLLBACK1[🔄 Rollback]
    CHECK_10 -->|Yes| CANARY_50[Canary: 50% Traffic<br/>2 Days]
    
    CANARY_50 --> CHECK_50{Metrics OK?}
    CHECK_50 -->|No| ROLLBACK2[🔄 Rollback]
    CHECK_50 -->|Yes| CANARY_100[Canary: 100% Traffic]
    
    CANARY_100 --> CHECK_100{Metrics OK?}
    CHECK_100 -->|No| ROLLBACK3[🔄 Rollback]
    CHECK_100 -->|Yes| SUCCESS[✅ Production Deployed]
    
    SUCCESS --> MONITOR[Monitor 48 Hours]
    ROLLBACK1 --> ARCHIVE[Archive Failed Version]
    ROLLBACK2 --> ARCHIVE
    ROLLBACK3 --> ARCHIVE
    
    style START fill:#E3F2FD
    style SUCCESS fill:#4CAF50
    style FAIL1 fill:#F44336
    style FAIL2 fill:#F44336
    style ROLLBACK1 fill:#FF9800
    style ROLLBACK2 fill:#FF9800
    style ROLLBACK3 fill:#FF9800
```

**Pipeline Stages:**
1. **Lint & Test**: Code quality, unit tests
2. **Validate**: Notebook syntax, model validation
3. **Deploy Staging**: Auto-deploy on develop branch
4. **Deploy Production**: Manual approval + canary deployment
5. **Canary Phases**: 10% → 50% → 100% with monitoring
6. **Rollback**: Automatic on failure

---

## 8. Model Lifecycle

### Model Version Lifecycle State Diagram

```mermaid
stateDiagram-v2
    [*] --> Development: Model Training
    
    Development --> Staging: Register to MLflow<br/>+2% AUC Improvement
    
    Staging --> Shadow: Enable Shadow Mode<br/>1-2 Weeks Evaluation
    
    Shadow --> Canary: Shadow Metrics OK<br/>Manual Approval
    
    Canary --> Production: Canary Success<br/>10% → 50% → 100%
    
    Production --> Archived: New Model Promoted<br/>Or Performance Degrades
    
    Staging --> Archived: Failed Evaluation<br/>Or Rejected
    
    Shadow --> Archived: Poor Shadow Performance
    
    Canary --> Archived: Canary Failure<br/>Automatic Rollback
    
    Production --> Archived: Retired<br/>Or Replaced
    
    Archived --> [*]: End of Lifecycle
    
    note right of Development
        Hyperparameter Tuning
        Cross-Validation
        Baseline Comparison
    end note
    
    note right of Shadow
        Parallel Evaluation
        Zero Risk
        Real-world Data
    end note
    
    note right of Production
        Live Traffic
        Continuous Monitoring
        Alerting Enabled
    end note
```

**State Transitions:**
- **Development → Staging**: Model meets performance criteria
- **Staging → Shadow**: Approved for shadow testing
- **Shadow → Canary**: Shadow metrics acceptable
- **Canary → Production**: Gradual rollout successful
- **Any → Archived**: Failure or replacement

---

## 9. Component Interaction

### System Component Interaction Diagram

```mermaid
graph TB
    subgraph "External Systems"
        CRM[CRM System]
        WEB[Web Applications]
    end
    
    subgraph "API Gateway"
        API[FastAPI Service]
        AUTH[Authentication]
        RATE[Rate Limiting]
    end
    
    subgraph "Model Services"
        PROD_MODEL[Production Model]
        SHADOW_MODEL[Shadow Model]
        MLFLOW[MLflow Registry]
    end
    
    subgraph "Data Services"
        DELTA[Delta Lake]
        FEATURE_STORE[Feature Store]
        CACHE[Redis Cache]
    end
    
    subgraph "Monitoring Services"
        METRICS[Metrics Collector]
        DRIFT[Drift Detector]
        ALERTS[Alert Manager]
    end
    
    subgraph "Storage"
        PRED_LOG[Prediction Logs]
        AUDIT_LOG[Audit Logs]
        MODEL_ARTIFACTS[Model Artifacts]
    end
    
    CRM --> API
    WEB --> API
    API --> AUTH
    AUTH --> RATE
    RATE --> PROD_MODEL
    RATE --> SHADOW_MODEL
    
    PROD_MODEL --> MLFLOW
    SHADOW_MODEL --> MLFLOW
    MLFLOW --> MODEL_ARTIFACTS
    
    PROD_MODEL --> DELTA
    PROD_MODEL --> FEATURE_STORE
    PROD_MODEL --> CACHE
    
    PROD_MODEL --> METRICS
    SHADOW_MODEL --> METRICS
    METRICS --> DRIFT
    DRIFT --> ALERTS
    
    PROD_MODEL --> PRED_LOG
    API --> AUDIT_LOG
    
    style API fill:#2196F3
    style PROD_MODEL fill:#4CAF50
    style SHADOW_MODEL fill:#9C27B0
    style MLFLOW fill:#00BCD4
    style DRIFT fill:#FF9800
```

**Interaction Patterns:**
- **Synchronous**: API → Model → Response
- **Asynchronous**: Model → Logging → Monitoring
- **Caching**: Feature Store → Redis → Model
- **Event-Driven**: Metrics → Drift Detection → Alerts

---

## 📊 Diagram Usage Guide

### When to Use Each Diagram

| Diagram | Use Case | Audience |
|---------|----------|----------|
| **System Overview** | High-level presentation, executive summary | Executives, Stakeholders |
| **Deployment Architecture** | Technical implementation details | Engineers, Architects |
| **Monitoring Architecture** | Operations and monitoring setup | DevOps, ML Engineers |
| **Retraining Architecture** | Model lifecycle management | ML Engineers, Data Scientists |
| **API Request Flow** | API integration and debugging | Developers, Integration Teams |
| **Data Flow** | Data pipeline understanding | Data Engineers, Analysts |
| **CI/CD Pipeline** | Deployment process | DevOps, Release Managers |
| **Model Lifecycle** | Model versioning strategy | ML Engineers, Product Managers |
| **Component Interaction** | System design and architecture | Architects, Senior Engineers |

---

## 🔗 Related Documentation

- **Detailed Architecture**: `01_architecture/deployment_architecture.md`
- **Monitoring Details**: `01_architecture/monitoring_architecture.md`
- **Retraining Details**: `01_architecture/retraining_architecture.md`
- **Presentation**: `06_docs/presentation_slides.md`
- **Complete Guide**: `06_docs/detailed_readme.md`
- **Diagram Index**: `06_docs/DIAGRAM_INDEX.md`

---

## 📝 Notes

- All diagrams use **Mermaid** syntax and render in:
  - GitHub/GitLab markdown viewers
  - VS Code with Mermaid extension
  - Online: https://mermaid.live/
  - Documentation tools (MkDocs, Docusaurus, etc.)

- For **PowerPoint/PDF** conversion:
  - Use Mermaid Live Editor to export as PNG/SVG
  - Or use tools like `mermaid-cli` for batch conversion

---

**Last Updated**: 2025-01-05  
**Version**: 2.0  
**Maintained By**: ML Engineering Team

