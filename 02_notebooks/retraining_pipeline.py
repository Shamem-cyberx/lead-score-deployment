"""
RAKEZ Lead Scoring Model - Automated Retraining Pipeline
Databricks Notebook for Model Retraining

This notebook:
1. Triggers retraining based on drift or schedule
2. Trains new model with hyperparameter tuning
3. Evaluates model performance
4. Promotes model to staging/production via MLflow
"""

# Databricks notebook source
# MAGIC %md
# MAGIC # Automated Model Retraining Pipeline
# MAGIC 
# MAGIC This notebook handles automated model retraining and promotion.

# COMMAND ----------

# Import libraries
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
import xgboost as xgb
import optuna
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# COMMAND ----------

# Configuration
TRAINING_DATA_TABLE = "default.leads_gold"
MODEL_REGISTRY_NAME = "lead_scoring_model"
EXPERIMENT_NAME = "lead_scoring_retraining"
MIN_TRAINING_SAMPLES = 10000
MIN_IMPROVEMENT_AUC = 0.02  # 2% improvement required
MIN_IMPROVEMENT_BUSINESS = 0.05  # 5% business KPI improvement

# COMMAND ----------

def load_training_data(spark: SparkSession, table_name: str, months: int = 6):
    """
    Load training data from Delta table
    
    Args:
        spark: SparkSession
        table_name: Delta table name
        months: Number of months of data to use
    
    Returns:
        Tuple of (X, y) DataFrames
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        # Load data
        df = spark.read.table(table_name).filter(
            col("created_at") >= lit(cutoff_date) &
            col("converted").isNotNull()  # Only labeled data
        ).toPandas()
        
        if len(df) < MIN_TRAINING_SAMPLES:
            raise ValueError(f"Insufficient training data: {len(df)} < {MIN_TRAINING_SAMPLES}")
        
        logger.info(f"Loaded {len(df)} training samples")
        
        # Separate features and target
        feature_columns = [
            'company_size', 'industry', 'page_views', 'time_on_site',
            'form_completion_time', 'referral_source', 'hour_of_day',
            'day_of_week', 'is_weekend', 'engagement_score'
        ]
        
        # Select available features
        available_features = [col for col in feature_columns if col in df.columns]
        X = df[available_features]
        y = df['converted'].astype(int)
        
        return X, y, available_features
        
    except Exception as e:
        logger.error(f"Error loading training data: {str(e)}")
        raise

# COMMAND ----------

def prepare_features(X: pd.DataFrame):
    """
    Prepare features for training (same as inference pipeline)
    
    Args:
        X: Feature DataFrame
    
    Returns:
        Prepared feature DataFrame
    """
    X_prep = X.copy()
    
    # Handle missing values
    numeric_cols = X_prep.select_dtypes(include=[np.number]).columns
    X_prep[numeric_cols] = X_prep[numeric_cols].fillna(0)
    
    categorical_cols = X_prep.select_dtypes(include=['object']).columns
    X_prep[categorical_cols] = X_prep[categorical_cols].fillna('unknown')
    
    # Encode categorical variables (simplified - use proper encoding in production)
    for col in categorical_cols:
        if col in X_prep.columns:
            X_prep[col] = pd.Categorical(X_prep[col]).codes
    
    return X_prep

# COMMAND ----------

def train_model_with_hyperopt(X: pd.DataFrame, y: pd.Series, n_trials: int = 50):
    """
    Train model with hyperparameter optimization using Optuna
    
    Args:
        X: Feature DataFrame
        y: Target Series
        n_trials: Number of optimization trials
    
    Returns:
        Best model and hyperparameters
    """
    try:
        # Prepare features
        X_prep = prepare_features(X)
        
        # Time series split for cross-validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        def objective(trial):
            # Hyperparameter search space
            params = {
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
                'gamma': trial.suggest_float('gamma', 0, 0.5),
                'reg_alpha': trial.suggest_float('reg_alpha', 0, 1),
                'reg_lambda': trial.suggest_float('reg_lambda', 0, 1),
                'random_state': 42,
                'eval_metric': 'logloss'
            }
            
            # Cross-validation
            scores = []
            for train_idx, val_idx in tscv.split(X_prep):
                X_train, X_val = X_prep.iloc[train_idx], X_prep.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                model = xgb.XGBClassifier(**params)
                model.fit(X_train, y_train, 
                         eval_set=[(X_val, y_val)],
                         early_stopping_rounds=10,
                         verbose=False)
                
                y_pred_proba = model.predict_proba(X_val)[:, 1]
                score = roc_auc_score(y_val, y_pred_proba)
                scores.append(score)
            
            return np.mean(scores)
        
        # Run optimization
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
        
        # Train final model with best parameters
        best_params = study.best_params
        best_params['random_state'] = 42
        best_params['eval_metric'] = 'logloss'
        
        final_model = xgb.XGBClassifier(**best_params)
        final_model.fit(X_prep, y)
        
        logger.info(f"Best AUC: {study.best_value:.4f}")
        logger.info(f"Best parameters: {best_params}")
        
        return final_model, best_params, X_prep.columns.tolist()
        
    except Exception as e:
        logger.error(f"Error in hyperparameter optimization: {str(e)}")
        raise

# COMMAND ----------

def evaluate_model(model, X: pd.DataFrame, y: pd.Series, feature_columns: list):
    """
    Evaluate model performance
    
    Args:
        model: Trained model
        X: Feature DataFrame
        y: Target Series
        feature_columns: List of feature names
    
    Returns:
        Dictionary with evaluation metrics
    """
    try:
        X_prep = prepare_features(X)
        X_prep = X_prep[feature_columns]  # Ensure same features
        
        # Predictions
        y_pred_proba = model.predict_proba(X_prep)[:, 1]
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Calculate metrics
        auc = roc_auc_score(y, y_pred_proba)
        precision = precision_score(y, y_pred, zero_division=0)
        recall = recall_score(y, y_pred, zero_division=0)
        f1 = f1_score(y, y_pred, zero_division=0)
        
        metrics = {
            'auc': auc,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'positive_rate': y.mean()
        }
        
        logger.info(f"Model Evaluation - AUC: {auc:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")
        return metrics
        
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        raise

# COMMAND ----------

def compare_with_production(model, X: pd.DataFrame, y: pd.Series, feature_columns: list):
    """
    Compare new model with production model
    
    Args:
        model: New trained model
        X: Feature DataFrame
        y: Target Series
        feature_columns: List of feature names
    
    Returns:
        Dictionary with comparison results
    """
    try:
        # Load production model
        try:
            production_model = mlflow.sklearn.load_model(
                f"models:/{MODEL_REGISTRY_NAME}/Production"
            )
        except:
            logger.warning("No production model found, skipping comparison")
            return {'improvement_auc': 0, 'improvement_f1': 0}
        
        # Evaluate both models
        new_metrics = evaluate_model(model, X, y, feature_columns)
        
        X_prep = prepare_features(X)
        X_prep = X_prep[feature_columns]
        prod_pred_proba = production_model.predict_proba(X_prep)[:, 1]
        prod_auc = roc_auc_score(y, prod_pred_proba)
        prod_pred = (prod_pred_proba >= 0.5).astype(int)
        prod_f1 = f1_score(y, prod_pred, zero_division=0)
        
        improvement_auc = new_metrics['auc'] - prod_auc
        improvement_f1 = new_metrics['f1_score'] - prod_f1
        
        comparison = {
            'production_auc': prod_auc,
            'new_model_auc': new_metrics['auc'],
            'improvement_auc': improvement_auc,
            'production_f1': prod_f1,
            'new_model_f1': new_metrics['f1_score'],
            'improvement_f1': improvement_f1,
            'meets_threshold': improvement_auc >= MIN_IMPROVEMENT_AUC
        }
        
        logger.info(f"Model Comparison:")
        logger.info(f"  Production AUC: {prod_auc:.4f}")
        logger.info(f"  New Model AUC: {new_metrics['auc']:.4f}")
        logger.info(f"  Improvement: {improvement_auc:.4f}")
        
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing with production: {str(e)}")
        raise

# COMMAND ----------

def register_model_to_mlflow(model, metrics: dict, hyperparams: dict, 
                             feature_columns: list, stage: str = "Staging"):
    """
    Register model to MLflow Model Registry
    
    Args:
        model: Trained model
        metrics: Evaluation metrics
        hyperparams: Hyperparameters
        feature_columns: List of feature names
        stage: Model stage (Staging or Production)
    """
    try:
        # Set MLflow experiment
        mlflow.set_experiment(EXPERIMENT_NAME)
        
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(hyperparams)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.xgboost.log_model(model, "model")
            
            # Log feature list
            mlflow.log_param("feature_columns", ",".join(feature_columns))
            mlflow.log_param("training_date", datetime.now().isoformat())
            
            # Register model
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
            registered_model = mlflow.register_model(model_uri, MODEL_REGISTRY_NAME)
            
            # Transition to stage
            client = mlflow.tracking.MlflowClient()
            client.transition_model_version_stage(
                name=MODEL_REGISTRY_NAME,
                version=registered_model.version,
                stage=stage
            )
            
            logger.info(f"Model registered to {stage} stage: version {registered_model.version}")
            return registered_model.version
            
    except Exception as e:
        logger.error(f"Error registering model to MLflow: {str(e)}")
        raise

# COMMAND ----------

def check_retraining_trigger(spark: SparkSession):
    """
    Check if retraining should be triggered
    
    Args:
        spark: SparkSession
    
    Returns:
        Boolean indicating if retraining should proceed
    """
    try:
        # Check drift detection results
        drift_table = "default.drift_detection_results"
        try:
            latest_drift = spark.read.table(drift_table) \
                .orderBy(col("detection_timestamp").desc()) \
                .limit(1) \
                .collect()
            
            if latest_drift:
                drift_row = latest_drift[0]
                psi = drift_row.get('psi', 0) or 0
                
                if psi > 0.25:  # Significant drift
                    logger.info(f"Drift detected (PSI={psi:.4f}), triggering retraining")
                    return True
        except:
            logger.info("No drift detection results found, proceeding with scheduled retraining")
        
        # Default: proceed with scheduled retraining
        return True
        
    except Exception as e:
        logger.error(f"Error checking retraining trigger: {str(e)}")
        return True  # Default to True for scheduled retraining

# COMMAND ----------

# Main execution
if __name__ == "__main__":
    try:
        spark = SparkSession.builder.appName("ModelRetraining").getOrCreate()
        
        logger.info("=" * 50)
        logger.info("Starting Model Retraining Pipeline")
        logger.info("=" * 50)
        
        # Check if retraining should be triggered
        if not check_retraining_trigger(spark):
            logger.info("Retraining not triggered. Exiting.")
            exit(0)
        
        # Load training data
        X, y, feature_columns = load_training_data(spark, TRAINING_DATA_TABLE, months=6)
        
        # Split into train and validation
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Train model with hyperparameter optimization
        model, best_params, feature_list = train_model_with_hyperopt(
            X_train, y_train, n_trials=50
        )
        
        # Evaluate on validation set
        val_metrics = evaluate_model(model, X_val, y_val, feature_list)
        
        # Compare with production
        comparison = compare_with_production(model, X_val, y_val, feature_list)
        
        # Check if model meets improvement threshold
        if comparison.get('meets_threshold', False):
            logger.info("Model meets improvement threshold, registering to Staging")
            
            # Combine all metrics
            all_metrics = {**val_metrics, **comparison}
            
            # Register to MLflow
            model_version = register_model_to_mlflow(
                model, all_metrics, best_params, feature_list, stage="Staging"
            )
            
            logger.info(f"Model registered successfully. Version: {model_version}")
            logger.info("Next step: Manual review and promotion to Production")
        else:
            logger.warning("Model does not meet improvement threshold. Not registering.")
            logger.warning(f"Required improvement: {MIN_IMPROVEMENT_AUC:.4f}, Actual: {comparison.get('improvement_auc', 0):.4f}")
        
        logger.info("=" * 50)
        logger.info("Retraining Pipeline Completed")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Fatal error in retraining pipeline: {str(e)}")
        raise

