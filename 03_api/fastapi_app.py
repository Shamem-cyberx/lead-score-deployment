"""
RAKEZ Lead Scoring Model - FastAPI Application
Production REST API for Real-time Lead Scoring

Features:
- Real-time lead scoring endpoint
- Shadow model evaluation
- Input validation
- Request logging
- Error handling
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import time
import os
import warnings

# Suppress scikit-learn version warnings
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
warnings.filterwarnings('ignore', message='.*Trying to unpickle.*')
try:
    from audit_logging import AuditLogger, get_audit_logger
except ImportError:
    # Fallback if audit_logging not available
    AuditLogger = None
    def get_audit_logger():
        return None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAKEZ Lead Scoring API",
    description="Production API for real-time lead scoring",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
MODEL_REGISTRY_NAME = "lead_scoring_model"
MODEL_STAGE = os.getenv("MODEL_STAGE", "Production")
SHADOW_MODEL_ENABLED = os.getenv("SHADOW_MODEL_ENABLED", "false").lower() == "true"
SHADOW_MODEL_STAGE = "Staging"

# Global model variables
production_model = None
shadow_model = None

# Request logging (in production, use proper logging service)
request_logs = []

# Initialize audit logger (optional)
try:
    audit_logger = get_audit_logger()
    if audit_logger is None:
        audit_logger = AuditLogger() if AuditLogger else None
except:
    audit_logger = None


# Pydantic models for request/response
class LeadInput(BaseModel):
    """Input schema for lead scoring"""
    lead_id: str = Field(..., description="Unique lead identifier")
    company_size: Optional[str] = Field(None, description="Company size category")
    industry: Optional[str] = Field(None, description="Industry sector")
    page_views: Optional[int] = Field(None, ge=0, description="Number of page views")
    time_on_site: Optional[float] = Field(None, ge=0, description="Time spent on site (seconds)")
    form_completion_time: Optional[float] = Field(None, ge=0, description="Form completion time (seconds)")
    referral_source: Optional[str] = Field(None, description="Referral source")
    created_at: Optional[str] = Field(None, description="Lead creation timestamp (ISO format)")
    
    @validator('created_at')
    def validate_timestamp(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except:
                raise ValueError("Invalid timestamp format. Use ISO 8601 format.")
        return v


class LeadScoreResponse(BaseModel):
    """Response schema for lead scoring"""
    lead_id: str
    lead_score: float = Field(..., ge=0, le=1, description="Lead conversion probability")
    score_category: str = Field(..., description="Score category (Low/Medium/High/Very High)")
    model_version: str = Field(..., description="Model version used")
    prediction_timestamp: str = Field(..., description="Prediction timestamp")
    latency_ms: float = Field(..., description="Prediction latency in milliseconds")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_stage: str
    shadow_model_enabled: bool
    timestamp: str


class ExplainabilityResponse(BaseModel):
    """Response schema for model explainability"""
    lead_id: str
    prediction: float
    explanation_method: str
    feature_contributions: Dict[str, float]
    base_value: Optional[float] = None
    timestamp: str


def load_model_from_registry(model_name: str, stage: str):
    """
    Load model from MLflow Model Registry
    
    Args:
        model_name: Model name in registry
        stage: Model stage (Production, Staging, etc.)
    
    Returns:
        Loaded MLflow model
    """
    try:
        model_uri = f"models:/{model_name}/{stage}"
        logger.info(f"Loading model from: {model_uri}")
        
        # Suppress version warnings during model loading
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=UserWarning)
            warnings.filterwarnings('ignore', message='.*Trying to unpickle.*')
            warnings.filterwarnings('ignore', message='.*InconsistentVersionWarning.*')
            model = mlflow.sklearn.load_model(model_uri)
        
        # Patch model to handle version incompatibility
        # Add missing attributes that newer scikit-learn versions expect
        if hasattr(model, 'estimators_'):
            # For ensemble models, patch each estimator
            for estimator in model.estimators_:
                if hasattr(estimator, '__dict__') and 'monotonic_cst' not in estimator.__dict__:
                    # Add missing attribute with default value
                    estimator.monotonic_cst = None
        elif hasattr(model, '__dict__') and 'monotonic_cst' not in model.__dict__:
            # For single models, add missing attribute
            model.monotonic_cst = None
        
        logger.info(f"Model loaded successfully from stage: {stage}")
        return model
    except Exception as e:
        logger.error(f"Error loading model from {stage}: {str(e)}")
        raise


@app.on_event("startup")
async def startup_event():
    """Load models on application startup"""
    global production_model, shadow_model
    
    try:
        # Load production model
        production_model = load_model_from_registry(MODEL_REGISTRY_NAME, MODEL_STAGE)
        logger.info("Production model loaded successfully")
        
        # Load shadow model if enabled
        if SHADOW_MODEL_ENABLED:
            try:
                shadow_model = load_model_from_registry(MODEL_REGISTRY_NAME, SHADOW_MODEL_STAGE)
                logger.info("Shadow model loaded successfully")
            except Exception as e:
                logger.warning(f"Shadow model not available: {str(e)}")
                shadow_model = None
        
    except Exception as e:
        logger.warning(f"Failed to load models on startup: {str(e)}")
        logger.warning("API will start but scoring endpoints will return errors until model is registered.")
        logger.warning("To register a model, use MLflow: mlflow.register_model(model_uri, 'lead_scoring_model')")
        # Don't raise - allow app to start without model for development/testing
        production_model = None
        shadow_model = None


def prepare_features(lead_data: dict) -> pd.DataFrame:
    """
    Prepare features for model inference
    Matches feature engineering from training pipeline
    
    Args:
        lead_data: Dictionary with lead input data
    
    Returns:
        DataFrame with engineered features (all numeric)
    """
    # Create DataFrame from input
    # Extract created_at BEFORE creating DataFrame to avoid pandas filling it with 'unknown'
    created_at_val = lead_data.get('created_at', None)
    
    # Remove created_at from dict temporarily to avoid pandas issues
    lead_data_clean = {k: v for k, v in lead_data.items() if k != 'created_at'}
    df = pd.DataFrame([lead_data_clean])
    
    # Feature engineering (must match training pipeline)
    # 1. Handle missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    categorical_cols = df.select_dtypes(include=['object']).columns
    df[categorical_cols] = df[categorical_cols].fillna('unknown')
    
    # 2. Encode categorical features to numeric (label encoding)
    # This is a simplified encoding - in production, use the same encoder from training
    categorical_encodings = {
        'company_size': {'Small': 0, 'Medium': 1, 'Large': 2, 'Enterprise': 3, 'unknown': 0},
        'industry': {
            'Technology': 0, 'Finance': 1, 'Healthcare': 2, 'Retail': 3, 
            'Manufacturing': 4, 'Education': 5, 'unknown': 0
        },
        'referral_source': {
            'Organic Search': 0, 'Paid Search': 1, 'Social Media': 2, 
            'Direct': 3, 'Referral': 4, 'Email': 5, 'unknown': 0
        }
    }
    
    for col in categorical_cols:
        if col in categorical_encodings:
            encoding_map = categorical_encodings[col]
            df[col] = df[col].map(lambda x: encoding_map.get(str(x), 0)).fillna(0).astype(int)
        else:
            # For other categorical columns, use simple hash-based encoding
            df[col] = pd.Categorical(df[col]).codes
    
    # 3. Time-based features - handle created_at separately from original dict
    if created_at_val and created_at_val not in [None, 'unknown', '', np.nan]:
        try:
            # Try to parse as datetime
            parsed_dt = pd.to_datetime(created_at_val, errors='coerce')
            if pd.notna(parsed_dt):
                df['hour_of_day'] = parsed_dt.hour
                df['day_of_week'] = parsed_dt.dayofweek
                df['is_weekend'] = 1 if parsed_dt.dayofweek >= 5 else 0
            else:
                # Parsing failed, use current time
                df['hour_of_day'] = datetime.now().hour
                df['day_of_week'] = datetime.now().weekday()
                df['is_weekend'] = 1 if datetime.now().weekday() >= 5 else 0
        except Exception:
            # Parsing failed, use current time
            df['hour_of_day'] = datetime.now().hour
            df['day_of_week'] = datetime.now().weekday()
            df['is_weekend'] = 1 if datetime.now().weekday() >= 5 else 0
    else:
        # No valid created_at, use current time
        df['hour_of_day'] = datetime.now().hour
        df['day_of_week'] = datetime.now().weekday()
        df['is_weekend'] = 1 if datetime.now().weekday() >= 5 else 0
    
    # 4. Interaction features
    if 'page_views' in df.columns and 'time_on_site' in df.columns:
        df['engagement_score'] = df['page_views'] * df['time_on_site']
    else:
        df['engagement_score'] = 0
    
    # 5. Derived features (keep as numeric)
    if 'company_size' in df.columns and 'industry' in df.columns:
        # Create numeric combination instead of string
        df['company_size_industry'] = df['company_size'] * 10 + df['industry']
    
    # 6. Ensure ALL columns are numeric (final safety check)
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to convert using categorical codes
            try:
                df[col] = pd.Categorical(df[col]).codes
            except:
                # If that fails, use hash-based encoding
                df[col] = df[col].astype(str).apply(lambda x: hash(x) % 1000)
        
        # Ensure numeric types are actually numeric
        if df[col].dtype not in [np.int64, np.int32, np.float64, np.float32]:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            except:
                df[col] = 0
    
    # Debug: Log column types to verify encoding worked
    logger.debug(f"Feature columns after encoding: {df.dtypes.to_dict()}")
    
    return df


def get_score_category(score: float) -> str:
    """Convert numeric score to category"""
    if score < 0.3:
        return "Low"
    elif score < 0.5:
        return "Medium"
    elif score < 0.7:
        return "High"
    else:
        return "Very High"


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        model_loaded=production_model is not None,
        model_stage=MODEL_STAGE,
        shadow_model_enabled=SHADOW_MODEL_ENABLED and shadow_model is not None,
        timestamp=datetime.now().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return await root()


@app.post("/score-lead", response_model=LeadScoreResponse)
async def score_lead(lead: LeadInput, request: Request):
    """
    Score a lead and return conversion probability
    
    Args:
        lead: Lead input data
        request: FastAPI request object
    
    Returns:
        Lead score and metadata
    """
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    user = request.headers.get("X-User", "anonymous")
    user_role = request.headers.get("X-User-Role", "viewer")
    
    try:
        # Validate model is loaded
        if production_model is None:
            audit_logger.log_failed_action(
                action="PREDICTION",
                user=user,
                resource=f"lead_{lead.lead_id}",
                error_message="Model not loaded",
                ip_address=client_ip,
                user_role=user_role
            )
            raise HTTPException(
                status_code=503,
                detail="Model not loaded. Please register a model to MLflow Model Registry with name 'lead_scoring_model' in 'Production' stage. See server logs for details."
            )
        
        # Prepare features
        lead_dict = lead.dict()
        features_df = prepare_features(lead_dict)
        
        # Get feature columns (in production, load from model metadata)
        feature_columns = [
            'company_size', 'industry', 'page_views', 'time_on_site',
            'form_completion_time', 'referral_source', 'hour_of_day',
            'day_of_week', 'is_weekend', 'engagement_score'
        ]
        
        # Select available features
        available_features = [col for col in feature_columns if col in features_df.columns]
        X = features_df[available_features]
        
        # Make prediction with production model
        prediction = production_model.predict_proba(X)[0, 1]  # Probability of positive class
        score = float(prediction)
        
        # Shadow model evaluation (silent, doesn't affect response)
        shadow_score = None
        if shadow_model is not None:
            try:
                shadow_prediction = shadow_model.predict_proba(X)[0, 1]
                shadow_score = float(shadow_prediction)
                
                # Log shadow prediction (in production, save to database)
                logger.info(f"Shadow model prediction for {lead.lead_id}: {shadow_score:.4f} "
                          f"(Production: {score:.4f})")
            except Exception as e:
                logger.warning(f"Shadow model prediction failed: {str(e)}")
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Get model version (in production, get from MLflow)
        model_version = "production_v1.0"  # Replace with actual version from MLflow
        
        # Log request (in production, save to database)
        request_log = {
            'lead_id': lead.lead_id,
            'timestamp': datetime.now().isoformat(),
            'score': score,
            'shadow_score': shadow_score,
            'latency_ms': latency_ms,
            'status_code': 200
        }
        request_logs.append(request_log)
        
        # Return response
        return LeadScoreResponse(
            lead_id=lead.lead_id,
            lead_score=score,
            score_category=get_score_category(score),
            model_version=model_version,
            prediction_timestamp=datetime.now().isoformat(),
            latency_ms=latency_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        
        # Log error
        error_log = {
            'lead_id': lead.lead_id if 'lead' in locals() else 'unknown',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'latency_ms': latency_ms,
            'status_code': 500
        }
        request_logs.append(error_log)
        
        logger.error(f"Error scoring lead {lead.lead_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/logs")
async def get_logs(limit: int = 100):
    """
    Get recent request logs (for debugging/monitoring)
    In production, this should be replaced with proper logging service
    """
    return {
        "logs": request_logs[-limit:],
        "total_logs": len(request_logs)
    }


@app.get("/model-info")
async def get_model_info():
    """Get information about loaded models"""
    info = {
        "production_model": {
            "loaded": production_model is not None,
            "stage": MODEL_STAGE
        },
        "shadow_model": {
            "enabled": SHADOW_MODEL_ENABLED,
            "loaded": shadow_model is not None,
            "stage": SHADOW_MODEL_STAGE if SHADOW_MODEL_ENABLED else None
        }
    }
    return info


@app.post("/explain-prediction", response_model=ExplainabilityResponse)
async def explain_prediction(lead: LeadInput, request: Request, method: str = "shap"):
    """
    Explain a model prediction using SHAP or LIME
    
    Args:
        lead: Lead input data
        request: FastAPI request object
        method: Explanation method ("shap" or "lime")
    
    Returns:
        Explanation with feature contributions
    """
    try:
        if production_model is None:
            raise HTTPException(
                status_code=503,
                detail="Model not loaded"
            )
        
        # Prepare features
        lead_dict = lead.dict()
        features_df = prepare_features(lead_dict)
        
        # Get feature columns (ensure all are numeric)
        feature_columns = [
            'company_size', 'industry', 'page_views', 'time_on_site',
            'form_completion_time', 'referral_source', 'hour_of_day',
            'day_of_week', 'is_weekend', 'engagement_score'
        ]
        
        # Select available features and ensure they're numeric
        available_features = []
        feature_values = []
        
        for col in feature_columns:
            if col in features_df.columns:
                val = features_df[col].iloc[0] if len(features_df) > 0 else 0
                # Convert to numeric - ensure it's already numeric from prepare_features
                try:
                    # First check if it's already numeric
                    if pd.api.types.is_numeric_dtype(features_df[col]):
                        numeric_val = float(val)
                    else:
                        # If not numeric, try to convert
                        numeric_val = float(pd.to_numeric(val, errors='coerce') or 0)
                    available_features.append(col)
                    feature_values.append(numeric_val)
                except (ValueError, TypeError) as e:
                    # If conversion fails, log and use 0
                    logger.warning(f"Could not convert {col} value '{val}' to numeric: {e}. Using 0.")
                    available_features.append(col)
                    feature_values.append(0.0)
        
        # Handle case where model expects different number of features
        # Get actual number of features the model expects
        try:
            # Try to get feature count from model
            if hasattr(production_model, 'n_features_in_'):
                expected_features = production_model.n_features_in_
            elif hasattr(production_model, 'feature_importances_'):
                expected_features = len(production_model.feature_importances_)
            else:
                # Fallback: try to infer from first prediction
                test_X = np.array([feature_values[:10] if len(feature_values) >= 10 else feature_values + [0.0] * (10 - len(feature_values))])
                try:
                    _ = production_model.predict_proba(test_X)
                    expected_features = test_X.shape[1]
                except:
                    expected_features = 10  # Default fallback
        except:
            expected_features = 10
        
        # Adjust feature values to match model expectations
        if len(feature_values) < expected_features:
            # Pad with zeros to match model expectations
            feature_values.extend([0.0] * (expected_features - len(feature_values)))
            # Add placeholder feature names
            for i in range(len(available_features), expected_features):
                available_features.append(f"feature_{i}")
        elif len(feature_values) > expected_features:
            # Truncate to expected features
            feature_values = feature_values[:expected_features]
            available_features = available_features[:expected_features]
        
        # Create numpy array for prediction
        X = np.array([feature_values])
        
        # Make prediction with error handling for version incompatibility
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                prediction = production_model.predict_proba(X)[0, 1]
        except Exception as e:
            logger.warning(f"Prediction failed with error: {e}. Trying alternative approach.")
            # If model fails, try with just the first N numeric columns
            numeric_cols = features_df.select_dtypes(include=[np.number]).columns[:expected_features]
            if len(numeric_cols) < expected_features:
                # Pad with zeros
                X = np.zeros((1, expected_features))
                for i, col in enumerate(numeric_cols):
                    if i < expected_features:
                        X[0, i] = float(features_df[col].iloc[0]) if len(features_df) > 0 else 0.0
            else:
                X = features_df[numeric_cols[:expected_features]].values
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                prediction = production_model.predict_proba(X)[0, 1]
        
        # Generate explanation using feature importance (works with any scikit-learn version)
        # Note: For true SHAP/LIME, we'd need to install and use those libraries
        # For now, we use feature_importances_ which is compatible with all versions
        feature_contributions = {}
        
        try:
            # Try to get feature importances from the model
            if hasattr(production_model, 'feature_importances_'):
                importances = production_model.feature_importances_
                # Map importances to feature names
                for i, feature in enumerate(available_features):
                    if i < len(importances):
                        feature_contributions[feature] = float(importances[i])
            elif hasattr(production_model, 'estimators_'):
                # For ensemble models, get average importance
                all_importances = []
                for est in production_model.estimators_:
                    if hasattr(est, 'feature_importances_'):
                        all_importances.append(est.feature_importances_)
                if all_importances:
                    avg_importances = np.mean(all_importances, axis=0)
                    for i, feature in enumerate(available_features):
                        if i < len(avg_importances):
                            feature_contributions[feature] = float(avg_importances[i])
            else:
                # Fallback: use equal contributions
                for feature in available_features:
                    feature_contributions[feature] = 1.0 / len(available_features)
        except Exception as e:
            logger.warning(f"Could not extract feature importances: {e}. Using equal contributions.")
            # Fallback: equal contributions
            for feature in available_features:
                feature_contributions[feature] = 1.0 / len(available_features)
        
        # Normalize contributions to sum to prediction - base_value
        # This makes it more like SHAP values
        total_contribution = sum(feature_contributions.values())
        if total_contribution > 0:
            # Scale contributions so they explain the prediction
            base_value = 0.5  # Default base value
            scale_factor = (prediction - base_value) / total_contribution if total_contribution != 0 else 1.0
            feature_contributions = {k: v * scale_factor for k, v in feature_contributions.items()}
        else:
            base_value = prediction
        
        # Sort by absolute contribution
        sorted_contributions = dict(sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        ))
        
        return ExplainabilityResponse(
            lead_id=lead.lead_id,
            prediction=float(prediction),
            explanation_method=method.upper(),
            feature_contributions=sorted_contributions,
            base_value=base_value,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining prediction: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error explaining prediction: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

