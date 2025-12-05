# 🔬 Model Explainability Tab - Integrated in Dashboard

## ✅ What's New

The **Model Explainability** tab is now integrated directly into the dashboard! No need for separate terminals or scripts.

---

## 🚀 How to Use

### Step 1: Start the FastAPI Server

**Terminal 1** (Backend):
```powershell
cd "d:\sha projects\rakez\rakez-lead-scoring-deployment\03_api"
python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000
```

Wait for:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 2: Start the Dashboard

**Terminal 2** (Dashboard):
```powershell
cd "d:\sha projects\rakez\rakez-lead-scoring-deployment\05_dashboard"
python dash_dashboard.py
```

Open: `http://localhost:8050` or `http://127.0.0.1:8050`

### Step 3: Use the Explainability Tab

1. Click on the **"🔬 Model Explainability"** tab in the dashboard
2. Fill in the lead information:
   - Lead ID
   - Company Size
   - Industry
   - Page Views
   - Time on Site
   - Form Completion Time
   - Referral Source
3. Select explanation method: **SHAP** or **LIME**
4. Click **"Generate Explanation"**

---

## 📊 What You'll See

### 1. Prediction Summary
- **Prediction Score**: The model's conversion probability
- **Explanation Method**: SHAP or LIME
- **Base Value**: Baseline prediction

### 2. Feature Contributions Chart
- Interactive bar chart showing which features increase/decrease the prediction
- Green bars = positive contribution (increases prediction)
- Red bars = negative contribution (decreases prediction)

### 3. Detailed Feature Contributions Table
- Complete list of all features and their contributions
- Color-coded for easy understanding

---

## 🎯 Features

✅ **Integrated in Dashboard** - No separate terminal needed
✅ **Interactive Form** - Easy input of lead data
✅ **Real-time API Calls** - Connects to FastAPI backend
✅ **Visual Charts** - Plotly interactive charts
✅ **SHAP & LIME Support** - Choose your explanation method
✅ **Error Handling** - Clear messages if backend is down

---

## ⚠️ Requirements

1. **FastAPI server must be running** on `http://127.0.0.1:8000`
2. **Model must be registered** (run `python create_dummy_model.py` if needed)
3. **Dashboard must be running** on `http://localhost:8050`

---

## 🔧 Troubleshooting

### "Backend API is not running"
- Start the FastAPI server in Terminal 1
- Check that it's running on port 8000

### "Model not loaded"
- Run `python create_dummy_model.py` in the `03_api` directory
- Restart the FastAPI server

### "Cannot connect to API"
- Verify the server is running: `http://127.0.0.1:8000/health`
- Check firewall settings
- Ensure both are running on the same machine

---

## 📝 Example

**Input:**
- Lead ID: `test_lead_001`
- Company Size: `Medium`
- Industry: `Technology`
- Page Views: `15`
- Time on Site: `450.5 seconds`
- Form Completion Time: `120.0 seconds`
- Referral Source: `Organic Search`
- Method: `SHAP`

**Output:**
- Prediction: `0.7234` (72.34% conversion probability)
- Top contributing features:
  - `page_views`: +0.1500 (increases prediction)
  - `time_on_site`: +0.1200 (increases prediction)
  - `engagement_score`: +0.0800 (increases prediction)

---

**Enjoy exploring model explainability directly in the dashboard!** 🎉

