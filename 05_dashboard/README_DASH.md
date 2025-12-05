# 🚀 Plotly Dash Dashboard - Fast & Modern

## Quick Start

### 1. Install Dependencies
```bash
pip install dash dash-bootstrap-components plotly pandas
```

Or install all requirements:
```bash
pip install -r ../requirements.txt
```

### 2. Start Dashboard
```bash
# Windows
start_dash.bat

# Linux/Mac
chmod +x start_dash.sh
./start_dash.sh

# Or directly
python dash_dashboard.py
```

### 3. Access Dashboard
Open your browser: **http://localhost:8050**

## Features

### ⚡ **Fast Performance**
- No full script re-execution
- Instant time range filtering
- Efficient in-memory caching
- Only updates what changed

### 🎨 **Modern UI**
- Bootstrap 5 styling
- Font Awesome icons
- Responsive design
- Professional appearance

### 📊 **Complete Monitoring**
- **Overview**: Key metrics at a glance
- **Drift Detection**: PSI by feature
- **Performance**: Latency and throughput
- **Business Metrics**: Conversion rates
- **Alerts**: Critical and warning alerts

## Time Range Filtering

The time range dropdown updates **instantly** - no loading loops!

- **Last 7 days**: Recent data
- **Last 30 days**: Monthly view
- **Last 90 days**: Quarterly view

## Data Sources

The dashboard automatically loads from:
- `sample_data/monitoring_metrics.csv`
- `sample_data/drift_detection.csv`
- `sample_data/leads_predictions.csv`
- `sample_data/lead_conversions.csv`

## Troubleshooting

### Dashboard won't start
```bash
# Check if port 8050 is available
netstat -ano | findstr :8050

# Or change port in dash_dashboard.py:
app.run(debug=True, host='0.0.0.0', port=8051)
```

### No data showing
- Ensure CSV files exist in `sample_data/` folder
- Check file permissions
- Verify CSV format is correct

### Slow performance
- Clear browser cache
- Restart dashboard
- Check data file sizes

## Comparison with Streamlit

| Feature | Streamlit | Dash |
|---------|-----------|------|
| Speed | Slow | **Fast** |
| Loading | Continuous | **Instant** |
| UI | Basic | **Modern** |
| Filtering | Slow | **Instant** |

## Why Dash?

1. **Faster**: No full script re-execution
2. **Better UI**: Bootstrap 5 styling
3. **More reliable**: No cache issues
4. **Production ready**: Used by many companies
5. **Open source**: MIT license

---

**Enjoy the fast, modern dashboard!** 🎉

