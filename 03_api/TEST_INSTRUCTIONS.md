# 🧪 How to Test the Explainability Endpoint

## Quick Start (2 Terminals)

### Terminal 1: Start the Server

**Option A: Using Batch File (Easiest)**
```
Double-click: start_server.bat
```

**Option B: Manual Command**
```powershell
cd "d:\sha projects\rakez\rakez-lead-scoring-deployment\03_api"
python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000
```

**Wait for this message:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

### Terminal 2: Run the Test

```powershell
cd "d:\sha projects\rakez\rakez-lead-scoring-deployment\03_api"
python test_while_running.py
```

---

## Expected Output

```
======================================================================
Testing Explainability Endpoint
======================================================================

1. Checking if server is running...
   ✅ Server is running!

2. Testing /explain-prediction with SHAP method...
   URL: http://127.0.0.1:8000/explain-prediction?method=shap

   Status Code: 200

   ✅ SUCCESS!

   📊 Explanation Results:
      Lead ID: test_001
      Prediction: 0.7234
      Method: SHAP
      Base Value: 0.5

   🔍 Feature Contributions (Top 10):
       1. page_views              : +0.1500
       2. time_on_site            : +0.1200
       3. engagement_score        : +0.0800
       ...

======================================================================
✅ Test completed successfully!
======================================================================
```

---

## Troubleshooting

### "Server is NOT running"
→ Start the server in Terminal 1 first (see above)

### "Model not loaded"
→ Run: `python create_dummy_model.py` (you already did this ✅)

### "Connection refused"
→ Server is not running. Check Terminal 1.

### Port 8000 already in use
→ Change port in start command: `--port 8001`

---

## Alternative: Test in Browser

1. Start server (Terminal 1)
2. Open browser: http://localhost:8000/docs
3. Find `/explain-prediction` endpoint
4. Click "Try it out"
5. Enter test data and click "Execute"

---

**That's it!** 🎉

