# 🚀 Quick Start Guide - RAKEZ Lead Scoring

## ⚡ Fastest Way to Start Everything

### **Option 1: Start Everything (Backend + Frontend)**
Double-click: **`START_ALL_SERVICES.bat`**

This will:
- ✅ Start Backend API (FastAPI) in a separate window
- ✅ Start Dashboard (Plotly Dash) in current window
- ✅ Auto-detect Python
- ✅ Install missing dependencies

---

### **Option 2: Start Backend Only**
Double-click: **`START_BACKEND_ONLY.bat`**

Opens: http://127.0.0.1:8000/docs

---

### **Option 3: Start Frontend Only**
Double-click: **`START_FRONTEND_ONLY.bat`**

Opens: http://localhost:8050

---

## 📋 Manual Commands

### **Start Backend (Terminal 1)**
```powershell
cd "D:\sha projects\rakez\rakez-lead-scoring-deployment\03_api"
py -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000
```

### **Start Frontend (Terminal 2)**
```powershell
cd "D:\sha projects\rakez\rakez-lead-scoring-deployment\05_dashboard"
py dash_dashboard.py
```

---

## 🌐 URLs After Starting

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:8050 | Main monitoring dashboard |
| **Backend API** | http://127.0.0.1:8000 | REST API |
| **API Docs** | http://127.0.0.1:8000/docs | Interactive API documentation |
| **Health Check** | http://127.0.0.1:8000/health | API health status |

---

## ✅ What Works

### **Dashboard (Works Standalone)**
- ✅ Overview tab
- ✅ Drift Detection tab
- ✅ Performance tab
- ✅ Business Metrics tab
- ✅ Alerts tab
- ⚠️ Explainability tab (needs backend)
- ⚠️ AI Insights tab (needs Ollama)

### **Backend API**
- ✅ Health check
- ✅ Lead scoring endpoint
- ✅ Model explainability (SHAP/LIME)
- ✅ Model info endpoint

---

## 🔧 Troubleshooting

### **"Python not found" Error**
**Solution**: The scripts auto-detect Python. If it fails:
1. Install Python from https://www.python.org/
2. Check "Add Python to PATH" during installation
3. Restart terminal after installation

### **"Module not found" Error**
**Solution**: Install dependencies:
```powershell
pip install fastapi uvicorn dash plotly pandas mlflow scikit-learn
```

### **Port Already in Use**
**Backend (8000)**: Change port in `03_api/start_server.bat`
**Frontend (8050)**: Change port in `05_dashboard/dash_dashboard.py` (line 1276)

### **Dashboard Shows No Data**
**Solution**: Check CSV files exist in `05_dashboard/sample_data/`

---

## 📊 Features Status

| Feature | Status | Requirements |
|---------|--------|--------------|
| Dashboard | ✅ Working | Python, Dash |
| Backend API | ✅ Working | Python, FastAPI |
| Explainability | ✅ Working | Backend running |
| AI Insights | ⚠️ Optional | Ollama installed |

---

## 🎯 Recommended Startup Order

1. **First Time**: Run `START_ALL_SERVICES.bat` (installs dependencies)
2. **Daily Use**: 
   - Terminal 1: `START_BACKEND_ONLY.bat`
   - Terminal 2: `START_FRONTEND_ONLY.bat`

---

**Ready to go! Just double-click `START_ALL_SERVICES.bat`** 🚀

