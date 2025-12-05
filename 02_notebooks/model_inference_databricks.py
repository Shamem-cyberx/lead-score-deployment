"""
RAKEZ Lead Scoring Model - Batch Inference Job
Databricks Notebook for Production Model Inference

This notebook:
1. Loads model from MLflow Model Registry
2. Performs batch inference on new leads
3. Logs predictions to Delta table
4. Updates CRM system with scores
"""

# Databricks notebook source
# MAGIC %md
# MAGIC # Lead Scoring Model - Batch Inference
# MAGIC 
# MAGIC This notebook runs scheduled batch inference on new leads from Delta Lake.

# COMMAND ----------

# Import libraries
import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# COMMAND ----------

# Configuration
MODEL_REGISTRY_NAME = "lead_scoring_model"
MODEL_STAGE = "Production"  # or "Staging" for testing
PREDICTION_TABLE = "default.lead_predictions"
LEAD_SOURCE_TABLE = "default.leads_silver"
CRM_TABLE = "default.crm_leads"

# COMMAND ----------

def load_production_model(model_name: str, stage: str = "Production"):
    """
    Load model from MLflow Model Registry
    
    Args:
        model_name: Name of the model in registry
        stage: Model stage (Production, Staging, Archived)
    
    Returns:
        Loaded MLflow model
    """
    try:
        model_uri = f"models:/{model_name}/{stage}"
        logger.info(f"Loading model from: {model_uri}")
        model = mlflow.sklearn.load_model(model_uri)
        logger.info(f"Model loaded successfully from stage: {stage}")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

# COMMAND ----------

def load_new_leads(spark: SparkSession, table_name: str, days_back: int = 1):
    """
    Load new leads from Delta table that haven't been scored yet
    
    Args:
        spark: SparkSession
        table_name: Delta table name
        days_back: Number of days to look back
    
    Returns:
        DataFrame with new leads
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Load leads that haven't been scored or are new
        leads_df = spark.read.table(table_name).filter(
            (col("created_at") >= lit(cutoff_date)) &
            (col("scored_at").isNull() | (col("scored_at") < col("updated_at")))
        )
        
        logger.info(f"Loaded {leads_df.count()} new leads for scoring")
        return leads_df
    except Exception as e:
        logger.error(f"Error loading leads: {str(e)}")
        raise

# COMMAND ----------

def prepare_features(df: pd.DataFrame):
    """
    Prepare features for model inference
    Matches the feature engineering from training
    
    Args:
        df: Input DataFrame with raw lead data
    
    Returns:
        DataFrame with engineered features
    """
    # Feature engineering (must match training pipeline)
    features_df = df.copy()
    
    # Example feature engineering steps
    # 1. Handle missing values
    numeric_cols = features_df.select_dtypes(include=[np.number]).columns
    features_df[numeric_cols] = features_df[numeric_cols].fillna(0)
    
    categorical_cols = features_df.select_dtypes(include=['object']).columns
    features_df[categorical_cols] = features_df[categorical_cols].fillna('unknown')
    
    # 2. Create derived features
    if 'company_size' in features_df.columns and 'industry' in features_df.columns:
        features_df['company_size_industry'] = (
            features_df['company_size'].astype(str) + '_' + 
            features_df['industry'].astype(str)
        )
    
    # 3. Time-based features
    if 'created_at' in features_df.columns:
        features_df['hour_of_day'] = pd.to_datetime(features_df['created_at']).dt.hour
        features_df['day_of_week'] = pd.to_datetime(features_df['created_at']).dt.dayofweek
        features_df['is_weekend'] = (features_df['day_of_week'] >= 5).astype(int)
    
    # 4. Interaction features
    if 'page_views' in features_df.columns and 'time_on_site' in features_df.columns:
        features_df['engagement_score'] = (
            features_df['page_views'] * features_df['time_on_site']
        )
    
    return features_df

# COMMAND ----------

def run_batch_inference(model, leads_df: pd.DataFrame):
    """
    Run batch inference on leads DataFrame
    
    Args:
        model: Trained MLflow model
        leads_df: DataFrame with leads to score
    
    Returns:
        DataFrame with predictions
    """
    try:
        # Prepare features
        features_df = prepare_features(leads_df)
        
        # Get feature columns (must match training)
        # In production, load feature list from MLflow model metadata
        feature_columns = [
            'company_size', 'industry', 'page_views', 'time_on_site',
            'form_completion_time', 'referral_source', 'hour_of_day',
            'day_of_week', 'is_weekend', 'engagement_score'
        ]
        
        # Select only available features
        available_features = [col for col in feature_columns if col in features_df.columns]
        X = features_df[available_features]
        
        # Make predictions
        logger.info(f"Running inference on {len(X)} leads")
        predictions = model.predict_proba(X)[:, 1]  # Probability of positive class
        
        # Create results DataFrame
        results_df = leads_df.copy()
        results_df['lead_score'] = predictions
        results_df['prediction_timestamp'] = datetime.now()
        results_df['model_version'] = mlflow.get_run(mlflow.active_run().info.run_id if mlflow.active_run() else None).info.run_id if mlflow.active_run() else "unknown"
        
        logger.info(f"Completed inference. Mean score: {predictions.mean():.4f}")
        return results_df
        
    except Exception as e:
        logger.error(f"Error during inference: {str(e)}")
        raise

# COMMAND ----------

def save_predictions(spark: SparkSession, predictions_df: pd.DataFrame, table_name: str):
    """
    Save predictions to Delta table
    
    Args:
        spark: SparkSession
        predictions_df: DataFrame with predictions
        table_name: Target Delta table name
    """
    try:
        # Convert pandas DataFrame to Spark DataFrame
        spark_df = spark.createDataFrame(predictions_df)
        
        # Write to Delta table (merge mode to handle updates)
        spark_df.write \
            .format("delta") \
            .mode("append") \
            .option("mergeSchema", "true") \
            .saveAsTable(table_name)
        
        logger.info(f"Saved {len(predictions_df)} predictions to {table_name}")
    except Exception as e:
        logger.error(f"Error saving predictions: {str(e)}")
        raise

# COMMAND ----------

def update_crm_system(spark: SparkSession, predictions_df: pd.DataFrame, crm_table: str):
    """
    Update CRM system with lead scores
    
    Args:
        spark: SparkSession
        predictions_df: DataFrame with predictions
        crm_table: CRM table name
    """
    try:
        # Select relevant columns for CRM
        crm_updates = predictions_df[['lead_id', 'lead_score', 'prediction_timestamp']].copy()
        
        # Convert to Spark DataFrame
        spark_df = spark.createDataFrame(crm_updates)
        
        # Update CRM table (upsert operation)
        spark_df.write \
            .format("delta") \
            .mode("overwrite") \
            .option("mergeSchema", "true") \
            .saveAsTable(crm_table)
        
        logger.info(f"Updated CRM system with {len(crm_updates)} lead scores")
    except Exception as e:
        logger.error(f"Error updating CRM: {str(e)}")
        raise

# COMMAND ----------

# Main execution
if __name__ == "__main__":
    try:
        # Initialize Spark
        spark = SparkSession.builder.appName("LeadScoringInference").getOrCreate()
        
        # Load production model
        logger.info("=" * 50)
        logger.info("Starting Lead Scoring Batch Inference")
        logger.info("=" * 50)
        
        model = load_production_model(MODEL_REGISTRY_NAME, MODEL_STAGE)
        
        # Load new leads
        leads_spark_df = load_new_leads(spark, LEAD_SOURCE_TABLE, days_back=1)
        
        if leads_spark_df.count() == 0:
            logger.info("No new leads to score. Exiting.")
        else:
            # Convert to Pandas for inference (or use Spark ML if model supports it)
            leads_pd_df = leads_spark_df.toPandas()
            
            # Run inference
            predictions_df = run_batch_inference(model, leads_pd_df)
            
            # Save predictions
            save_predictions(spark, predictions_df, PREDICTION_TABLE)
            
            # Update CRM
            update_crm_system(spark, predictions_df, CRM_TABLE)
            
            logger.info("=" * 50)
            logger.info("Batch Inference Completed Successfully")
            logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Fatal error in batch inference job: {str(e)}")
        raise

