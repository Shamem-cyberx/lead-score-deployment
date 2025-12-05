"""
Script to create a dummy model for testing purposes
This creates a simple sklearn model and registers it to MLflow
"""

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import numpy as np
import os

# Set MLflow tracking URI (defaults to local file system)
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "./mlruns"))

# Create a dummy dataset
X, y = make_classification(
    n_samples=1000,
    n_features=10,
    n_informative=5,
    n_redundant=2,
    n_classes=2,
    random_state=42
)

# Train a simple model
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X, y)

# Start MLflow run
with mlflow.start_run():
    # Log model parameters
    mlflow.log_param("n_estimators", 10)
    mlflow.log_param("random_state", 42)
    
    # Log some dummy metrics
    mlflow.log_metric("accuracy", 0.85)
    mlflow.log_metric("auc", 0.90)
    
    # Log the model
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="lead_scoring_model"
    )
    
    print("[OK] Model registered successfully!")
    print(f"Model URI: runs:/{mlflow.active_run().info.run_id}/model")
    print(f"Registered as: lead_scoring_model")

# Transition to Production stage
client = mlflow.tracking.MlflowClient()
try:
    latest_version = client.get_latest_versions("lead_scoring_model", stages=["None"])[0]
    client.transition_model_version_stage(
        name="lead_scoring_model",
        version=latest_version.version,
        stage="Production"
    )
    print(f"[OK] Model version {latest_version.version} transitioned to Production stage")
except Exception as e:
    print(f"[WARNING] Could not transition to Production: {e}")
    print("   You can manually transition it using MLflow UI or CLI")

print("\n[SUCCESS] Dummy model created and registered!")
print("   You can now start the FastAPI server and it will load this model.")

