"""
RAKEZ Lead Scoring Model - Model Explainability
Databricks Notebook for SHAP and LIME Explanations

This notebook provides:
1. SHAP (SHapley Additive exPlanations) for model interpretability
2. LIME (Local Interpretable Model-agnostic Explanations)
3. Feature importance analysis
4. Prediction explanations
"""

# Databricks notebook source
# MAGIC %md
# MAGIC # Model Explainability with SHAP and LIME
# MAGIC 
# MAGIC This notebook generates explanations for model predictions using SHAP and LIME.

# COMMAND ----------

# Import libraries
import pandas as pd
import numpy as np
import shap
from lime import lime_tabular
from lime.lime_tabular import LimeTabularExplainer
import mlflow
import mlflow.sklearn
import logging
from typing import Dict, List, Optional
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# COMMAND ----------

class ModelExplainability:
    """
    Class for generating model explanations using SHAP and LIME
    """
    
    def __init__(self, model, training_data: pd.DataFrame, feature_names: List[str]):
        """
        Initialize explainability tools
        
        Args:
            model: Trained ML model
            training_data: Training data used for model training
            feature_names: List of feature names
        """
        self.model = model
        self.training_data = training_data
        self.feature_names = feature_names
        
        # Initialize SHAP explainer
        try:
            if hasattr(model, 'predict_proba'):
                # Tree-based models (XGBoost, LightGBM, Random Forest)
                self.shap_explainer = shap.TreeExplainer(model)
            else:
                # Other models - use KernelExplainer (slower but more general)
                self.shap_explainer = shap.KernelExplainer(
                    model.predict_proba if hasattr(model, 'predict_proba') else model.predict,
                    training_data.sample(min(100, len(training_data)))  # Sample for speed
                )
            logger.info("SHAP explainer initialized successfully")
        except Exception as e:
            logger.warning(f"SHAP explainer initialization failed: {str(e)}")
            self.shap_explainer = None
        
        # Initialize LIME explainer
        try:
            self.lime_explainer = LimeTabularExplainer(
                training_data.values,
                feature_names=feature_names,
                mode='classification',
                training_labels=None,
                discretize_continuous=True
            )
            logger.info("LIME explainer initialized successfully")
        except Exception as e:
            logger.warning(f"LIME explainer initialization failed: {str(e)}")
            self.lime_explainer = None
    
    def explain_prediction_shap(self, instance: pd.DataFrame, num_features: int = 10) -> Dict:
        """
        Generate SHAP explanation for a single prediction
        
        Args:
            instance: Single instance to explain (DataFrame with one row)
            num_features: Number of top features to return
        
        Returns:
            Dictionary with SHAP explanation
        """
        if self.shap_explainer is None:
            return {"error": "SHAP explainer not initialized"}
        
        try:
            # Calculate SHAP values
            shap_values = self.shap_explainer.shap_values(instance)
            
            # Handle multi-class models (take first class if binary)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # Positive class for binary classification
            
            # Get base value (expected value)
            base_value = float(self.shap_explainer.expected_value)
            if isinstance(base_value, np.ndarray):
                base_value = float(base_value[1])  # Positive class
            
            # Get prediction
            prediction = self.model.predict_proba(instance)[0, 1] if hasattr(self.model, 'predict_proba') else self.model.predict(instance)[0]
            
            # Get feature contributions
            feature_contributions = {}
            for i, feature_name in enumerate(self.feature_names):
                if i < len(shap_values[0]):
                    feature_contributions[feature_name] = float(shap_values[0][i])
            
            # Sort by absolute contribution
            sorted_features = sorted(
                feature_contributions.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:num_features]
            
            return {
                "prediction": float(prediction),
                "base_value": base_value,
                "feature_contributions": dict(sorted_features),
                "explanation_method": "SHAP",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {str(e)}")
            return {"error": str(e)}
    
    def explain_prediction_lime(self, instance: pd.DataFrame, num_features: int = 10) -> Dict:
        """
        Generate LIME explanation for a single prediction
        
        Args:
            instance: Single instance to explain (DataFrame with one row)
            num_features: Number of top features to return
        
        Returns:
            Dictionary with LIME explanation
        """
        if self.lime_explainer is None:
            return {"error": "LIME explainer not initialized"}
        
        try:
            # Generate LIME explanation
            explanation = self.lime_explainer.explain_instance(
                instance.values[0],
                self.model.predict_proba if hasattr(self.model, 'predict_proba') else self.model.predict,
                num_features=num_features,
                top_labels=1
            )
            
            # Get prediction
            prediction = self.model.predict_proba(instance)[0, 1] if hasattr(self.model, 'predict_proba') else self.model.predict(instance)[0]
            
            # Extract feature contributions
            feature_contributions = {}
            explanation_list = explanation.as_list(label=1)  # Positive class
            for feature_name, contribution in explanation_list:
                feature_contributions[feature_name] = float(contribution)
            
            return {
                "prediction": float(prediction),
                "feature_contributions": feature_contributions,
                "explanation_method": "LIME",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating LIME explanation: {str(e)}")
            return {"error": str(e)}
    
    def explain_prediction(self, instance: pd.DataFrame, method: str = "shap", num_features: int = 10) -> Dict:
        """
        Generate explanation using specified method
        
        Args:
            instance: Single instance to explain
            method: "shap" or "lime"
            num_features: Number of top features to return
        
        Returns:
            Dictionary with explanation
        """
        if method.lower() == "shap":
            return self.explain_prediction_shap(instance, num_features)
        elif method.lower() == "lime":
            return self.explain_prediction_lime(instance, num_features)
        else:
            return {"error": f"Unknown method: {method}. Use 'shap' or 'lime'"}
    
    def get_global_feature_importance(self) -> Dict:
        """
        Get global feature importance from model
        
        Returns:
            Dictionary with feature importance scores
        """
        try:
            if hasattr(self.model, 'feature_importances_'):
                importances = self.model.feature_importances_
            elif hasattr(self.model, 'coef_'):
                importances = np.abs(self.model.coef_[0])
            else:
                return {"error": "Model does not support feature importance"}
            
            feature_importance = {}
            for i, feature_name in enumerate(self.feature_names):
                if i < len(importances):
                    feature_importance[feature_name] = float(importances[i])
            
            # Sort by importance
            sorted_importance = sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return {
                "feature_importance": dict(sorted_importance),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return {"error": str(e)}
    
    def generate_explanation_report(self, instance: pd.DataFrame) -> Dict:
        """
        Generate comprehensive explanation report with both SHAP and LIME
        
        Args:
            instance: Single instance to explain
        
        Returns:
            Dictionary with comprehensive explanation
        """
        report = {
            "instance_id": instance.index[0] if hasattr(instance.index, '__len__') else "unknown",
            "timestamp": datetime.now().isoformat(),
            "shap_explanation": self.explain_prediction_shap(instance),
            "lime_explanation": self.explain_prediction_lime(instance),
            "global_importance": self.get_global_feature_importance()
        }
        
        return report

# COMMAND ----------

# Example usage
if __name__ == "__main__":
    # Load model from MLflow
    model_uri = "models:/lead_scoring_model/Production"
    model = mlflow.sklearn.load_model(model_uri)
    
    # Load training data (example)
    # training_data = spark.read.table("default.leads_gold").toPandas()
    # feature_names = training_data.columns.tolist()
    
    # Initialize explainability
    # explainer = ModelExplainability(model, training_data, feature_names)
    
    # Explain a prediction
    # instance = training_data.iloc[[0]]  # First instance
    # explanation = explainer.explain_prediction(instance, method="shap")
    # print(json.dumps(explanation, indent=2))

