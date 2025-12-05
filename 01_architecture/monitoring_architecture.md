# Monitoring Architecture

## Overview
Comprehensive monitoring system for model performance, data quality, and system health.

## Mermaid Diagram

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
        DASH[Streamlit Dashboard<br/>Real-time Charts]
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

## Monitoring Components

### 1. Data Collection
- **API Request Logs**: All FastAPI requests logged with timestamps, inputs, outputs
- **Batch Job Logs**: Databricks job execution logs, processing times, record counts
- **Prediction Logs**: Centralized Delta table storing all predictions with metadata

### 2. Drift Detection
- **PSI (Population Stability Index)**: 
  - Threshold: PSI > 0.25 indicates significant drift
  - Calculated per feature and overall
- **KL Divergence**: Measures distribution shift between baseline and current data
- **Statistical Tests**: 
  - Kolmogorov-Smirnov test for continuous features
  - Chi-square test for categorical features

### 3. Performance Metrics
- **Latency Monitoring**: 
  - P50, P95, P99 percentiles
  - Target: P95 < 200ms
- **Throughput**: Requests per second capacity
- **Accuracy Metrics**: 
  - Conversion rate (leads → customers)
  - Precision/Recall for lead scoring
  - Business KPIs: Revenue per lead

### 4. Feature Monitoring
- **Feature Statistics**: 
  - Mean, standard deviation, min, max
  - Missing value percentage
  - Cardinality for categorical features
- **Distribution Comparison**: Baseline vs current distributions
- **Outlier Detection**: IQR method, Z-score analysis

### 5. Alerting System
- **Alert Rules**: 
  - PSI > 0.25: Warning
  - PSI > 0.5: Critical
  - Latency P95 > 500ms: Warning
  - Error rate > 1%: Critical
- **Notification Channels**: 
  - Slack: #ml-alerts channel
  - Email: ML team distribution list
  - PagerDuty: Critical production issues

### 6. Visualization
- **Streamlit Dashboard**: Real-time monitoring with interactive charts
- **Grafana**: System-level metrics (CPU, memory, network)
- **MLflow UI**: Experiment tracking and model versioning

## Monitoring Schedule

- **Real-time**: API latency, throughput, error rates
- **Hourly**: Feature statistics, distribution checks
- **Daily**: PSI calculation, KL divergence, accuracy metrics
- **Weekly**: Comprehensive drift report, model performance review

## Alert Escalation

1. **Level 1 (Info)**: Logged to dashboard, no notification
2. **Level 2 (Warning)**: Slack notification to #ml-alerts
3. **Level 3 (Critical)**: Email + Slack + PagerDuty alert

