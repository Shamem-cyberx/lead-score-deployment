"""Verify that the model is registered in MLflow"""
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()
models = client.search_registered_models()

print("Registered models in MLflow:")
if models:
    for model in models:
        print(f"  - {model.name}")
        if model.latest_versions:
            for version in model.latest_versions:
                print(f"    Version {version.version}: {version.current_stage}")
else:
    print("  No models found")

# Check specifically for our model
try:
    versions = client.get_latest_versions("lead_scoring_model", stages=["Production"])
    if versions:
        print(f"\n[OK] lead_scoring_model found in Production stage!")
        print(f"    Version: {versions[0].version}")
    else:
        print("\n[WARNING] lead_scoring_model not found in Production stage")
except Exception as e:
    print(f"\n[ERROR] {e}")

