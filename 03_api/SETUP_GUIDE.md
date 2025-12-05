# FastAPI Setup Guide

## ✅ Model Status

The dummy model has been created and registered to MLflow:
- **Model Name**: `lead_scoring_model`
- **Stage**: Production
- **Version**: 1

## Starting the Server

Now you can start the FastAPI server:

```bash
cd rakez-lead-scoring-deployment/03_api
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

The server should now start successfully and load the model!

## Testing the API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Or open in browser: http://localhost:8000/health

### 2. Interactive API Documentation
Open in browser: http://localhost:8000/docs

This provides a Swagger UI where you can test all endpoints interactively.

### 3. Score a Lead
```bash
curl -X POST "http://localhost:8000/score-lead" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "test_123",
    "company_size": "Medium",
    "industry": "Technology",
    "page_views": 15,
    "time_on_site": 300.5,
    "form_completion_time": 45.2,
    "referral_source": "Google"
  }'
```

## Model Loading Behavior

The FastAPI app has been updated to:
- ✅ Start successfully even if model is not found (logs warning)
- ✅ Return helpful error messages if model is missing
- ✅ Load model automatically on startup if available

## Creating Your Own Model

To replace the dummy model with your actual trained model:

1. Train your model using the retraining pipeline
2. Register it to MLflow:
   ```python
   import mlflow
   mlflow.sklearn.log_model(
       your_model,
       "model",
       registered_model_name="lead_scoring_model"
   )
   ```
3. Transition to Production stage
4. Restart the FastAPI server

## Troubleshooting

### Model Not Loading
- Check MLflow tracking URI is set correctly
- Verify model exists in registry: `mlflow models list`
- Check model stage is "Production"

### Server Won't Start
- Check if port 8000 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check logs for specific error messages

## Next Steps

1. ✅ Model is registered and ready
2. ✅ Server can start successfully
3. 🚀 Test the `/score-lead` endpoint
4. 🚀 Integrate with your CRM system
5. 🚀 Set up monitoring dashboard

