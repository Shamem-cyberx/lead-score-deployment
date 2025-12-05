# Streamlit Dashboard - Setup Guide

## Quick Start

```bash
cd rakez-lead-scoring-deployment/05_dashboard
streamlit run streamlit_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Demo Mode

The dashboard now works **without Databricks connection** in demo mode:
- Shows mock data for demonstration
- All visualizations work
- Perfect for testing and presentations

## Production Mode

To connect to real Databricks data:

1. **Set up Databricks connection** in the code:
   ```python
   spark = SparkSession.builder \
       .appName("StreamlitDashboard") \
       .config("spark.databricks.service.address", "your-workspace-url") \
       .config("spark.databricks.service.token", "your-token") \
       .getOrCreate()
   ```

2. **Ensure Delta tables exist**:
   - `default.drift_detection_results`
   - `default.monitoring_metrics`
   - `default.lead_predictions`
   - `default.lead_conversions`

## Features

- 📈 **Overview**: System metrics and performance trends
- 🔍 **Drift Detection**: PSI and distribution monitoring
- ⚡ **Performance**: Latency and throughput metrics
- 💰 **Business Metrics**: Conversion rates and score distributions
- 🚨 **Alerts**: System alerts and notifications

## Troubleshooting

### Dashboard shows "Demo Mode" warning
- This is normal if Databricks is not configured
- Mock data is displayed for demonstration
- Configure Databricks connection to use real data

### Charts not displaying
- Check that Plotly is installed: `pip install plotly`
- Refresh the page
- Check browser console for errors

### Slow loading
- Mock data loads instantly
- Real data loading depends on Databricks connection speed
- Consider caching for better performance

