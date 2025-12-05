# Sample Data Files

This folder contains realistic example data for the dashboard demonstration.

## Files

### 1. `leads_predictions.csv`
**50 lead predictions** with realistic data:
- Lead IDs, scores (0.35 - 0.91)
- Company sizes (Small, Medium, Large)
- Industries (Technology, Finance, Retail, Healthcare)
- Engagement metrics (page views, time on site, form completion)
- Referral sources (Google, LinkedIn, Direct, Email)
- Timestamps from Dec 1-8, 2024

### 2. `lead_conversions.csv`
**14 conversions** from the leads:
- Conversion dates (typically 3-14 days after lead creation)
- Revenue amounts ($3,500 - $15,000)
- Conversion types (Standard, Enterprise)
- Matches with high-scoring leads (scores > 0.70)

### 3. `monitoring_metrics.csv`
**7 days of metrics** (Dec 1-7, 2024):
- Latency metrics (P50, P95, P99)
- Throughput (18-24 req/s)
- Conversion rates (12.5% - 15.5%)
- Error rates (0.25% - 0.40%)
- Model performance (AUC: 0.87-0.91, F1: 0.78-0.82)

### 4. `drift_detection.csv`
**9 features** with drift metrics:
- PSI values (0.08 - 0.28)
- KL Divergence
- Statistical test results
- Some features showing warning-level drift (PSI > 0.25)

## Usage

The dashboard automatically loads these files when:
1. Databricks/Spark is not connected
2. Sample data files exist in this folder

## Data Characteristics

- **Realistic distributions**: Data follows expected patterns
- **Time-based**: Proper timestamps and date ranges
- **Correlations**: High scores correlate with conversions
- **Variety**: Multiple industries, company sizes, referral sources
- **Metrics trends**: Showing gradual improvements over time

## Customizing

You can replace these files with your own data:
- Keep the same column names
- Use CSV format
- Ensure proper date formats (YYYY-MM-DD HH:MM:SS)
- The dashboard will automatically detect and load them

## Notes

- These are example datasets for demonstration
- In production, data comes from Databricks Delta tables
- Sample data shows realistic business scenarios
- Conversion rate: ~28% (14 conversions from 50 leads)

