# ⚡ Quick Start - Plotly Dash Dashboard

## Why Dash Instead of Streamlit?

✅ **Faster** - No continuous loading  
✅ **Better UI** - Modern Bootstrap design  
✅ **Instant Updates** - Time range changes immediately  
✅ **Open Source** - MIT license  
✅ **Production Ready** - Used by many companies  

## Installation

```bash
# Install Dash
pip install dash plotly pandas

# Or install all requirements
pip install -r ../requirements.txt
```

## Start Dashboard

### Windows:
```bash
cd 05_dashboard
start_dash.bat
```

### Linux/Mac:
```bash
cd 05_dashboard
chmod +x start_dash.sh
./start_dash.sh
```

### Or directly:
```bash
python dash_dashboard.py
```

## Access Dashboard

Open browser: **http://localhost:8050**

## Features

- ⚡ **Fast loading** - No more continuous loading
- 🎨 **Modern UI** - Bootstrap 5 styling
- 📊 **All metrics** - Overview, Drift, Performance, Business, Alerts
- 🔄 **Instant filtering** - Time range updates immediately
- 📱 **Responsive** - Works on all devices

## Time Range Filter

**Works instantly!** No loading loops:
- Last 7 days
- Last 30 days  
- Last 90 days

## Troubleshooting

**Port already in use?**
```python
# Change port in dash_dashboard.py (last line):
app.run(debug=True, host='0.0.0.0', port=8051)
```

**No data showing?**
- Check `sample_data/` folder has CSV files
- Verify file permissions
- Check CSV format

---

**Enjoy the fast, modern dashboard!** 🚀

