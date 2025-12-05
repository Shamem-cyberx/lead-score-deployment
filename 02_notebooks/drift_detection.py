"""
RAKEZ Lead Scoring Model - Drift Detection
Databricks Notebook for Monitoring Data and Model Drift

This notebook:
1. Calculates PSI (Population Stability Index)
2. Computes KL Divergence for feature distributions
3. Detects statistical drift using KS test
4. Sends alerts when drift is detected
"""

# Databricks notebook source
# MAGIC %md
# MAGIC # Drift Detection and Monitoring
# MAGIC 
# MAGIC This notebook monitors data drift and model performance drift.

# COMMAND ----------

# Import libraries
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import ks_2samp, chi2_contingency
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp
import mlflow
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# COMMAND ----------

# Configuration
BASELINE_TABLE = "default.leads_baseline"  # Reference dataset
CURRENT_TABLE = "default.leads_silver"  # Current production data
DRIFT_RESULTS_TABLE = "default.drift_detection_results"
PSI_THRESHOLD_WARNING = 0.25
PSI_THRESHOLD_CRITICAL = 0.50
KL_THRESHOLD = 0.1
KS_PVALUE_THRESHOLD = 0.05

# COMMAND ----------

def calculate_psi(expected: pd.Series, actual: pd.Series, buckets: int = 10):
    """
    Calculate Population Stability Index (PSI)
    
    PSI Interpretation:
    - < 0.1: No significant change
    - 0.1 - 0.25: Moderate change (warning)
    - > 0.25: Significant change (drift detected)
    
    Args:
        expected: Baseline/reference distribution
        actual: Current distribution
        buckets: Number of bins for discretization
    
    Returns:
        PSI value
    """
    try:
        # Remove nulls
        expected = expected.dropna()
        actual = actual.dropna()
        
        if len(expected) == 0 or len(actual) == 0:
            return np.nan
        
        # Create bins based on expected distribution
        breakpoints = np.linspace(expected.min(), expected.max(), buckets + 1)
        breakpoints[0] = -np.inf
        breakpoints[-1] = np.inf
        
        # Calculate expected and actual distributions
        expected_percents = np.histogram(expected, bins=breakpoints)[0] / len(expected)
        actual_percents = np.histogram(actual, bins=breakpoints)[0] / len(actual)
        
        # Avoid division by zero
        expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
        actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
        
        # Calculate PSI
        psi = np.sum((actual_percents - expected_percents) * 
                     np.log(actual_percents / expected_percents))
        
        return psi
    except Exception as e:
        logger.error(f"Error calculating PSI: {str(e)}")
        return np.nan

# COMMAND ----------

def calculate_kl_divergence(expected: pd.Series, actual: pd.Series, bins: int = 50):
    """
    Calculate KL Divergence between two distributions
    
    Args:
        expected: Baseline distribution
        actual: Current distribution
        bins: Number of bins for histogram
    
    Returns:
        KL divergence value
    """
    try:
        # Remove nulls
        expected = expected.dropna()
        actual = actual.dropna()
        
        if len(expected) == 0 or len(actual) == 0:
            return np.nan
        
        # Create common bins
        min_val = min(expected.min(), actual.min())
        max_val = max(expected.max(), actual.max())
        bin_edges = np.linspace(min_val, max_val, bins + 1)
        
        # Calculate histograms
        expected_hist, _ = np.histogram(expected, bins=bin_edges)
        actual_hist, _ = np.histogram(actual, bins=bin_edges)
        
        # Normalize to probabilities
        expected_prob = expected_hist / expected_hist.sum()
        actual_prob = actual_hist / actual_hist.sum()
        
        # Avoid division by zero
        expected_prob = np.where(expected_prob == 0, 1e-10, expected_prob)
        actual_prob = np.where(actual_prob == 0, 1e-10, actual_prob)
        
        # Calculate KL divergence
        kl_div = np.sum(actual_prob * np.log(actual_prob / expected_prob))
        
        return kl_div
    except Exception as e:
        logger.error(f"Error calculating KL divergence: {str(e)}")
        return np.nan

# COMMAND ----------

def detect_numerical_drift(baseline: pd.Series, current: pd.Series):
    """
    Detect drift in numerical features using statistical tests
    
    Args:
        baseline: Baseline distribution
        current: Current distribution
    
    Returns:
        Dictionary with test results
    """
    results = {}
    
    try:
        # Kolmogorov-Smirnov test
        ks_statistic, ks_pvalue = ks_2samp(baseline.dropna(), current.dropna())
        results['ks_statistic'] = ks_statistic
        results['ks_pvalue'] = ks_pvalue
        results['ks_drift_detected'] = ks_pvalue < KS_PVALUE_THRESHOLD
        
        # Calculate PSI
        psi = calculate_psi(baseline, current)
        results['psi'] = psi
        results['psi_drift_detected'] = psi > PSI_THRESHOLD_WARNING
        
        # Calculate KL divergence
        kl_div = calculate_kl_divergence(baseline, current)
        results['kl_divergence'] = kl_div
        results['kl_drift_detected'] = kl_div > KL_THRESHOLD
        
        # Distribution statistics
        results['baseline_mean'] = baseline.mean()
        results['current_mean'] = current.mean()
        results['baseline_std'] = baseline.std()
        results['current_std'] = current.std()
        results['mean_shift'] = abs(results['current_mean'] - results['baseline_mean'])
        results['std_shift'] = abs(results['current_std'] - results['baseline_std'])
        
    except Exception as e:
        logger.error(f"Error in numerical drift detection: {str(e)}")
        results['error'] = str(e)
    
    return results

# COMMAND ----------

def detect_categorical_drift(baseline: pd.Series, current: pd.Series):
    """
    Detect drift in categorical features using Chi-square test
    
    Args:
        baseline: Baseline distribution
        current: Current distribution
    
    Returns:
        Dictionary with test results
    """
    results = {}
    
    try:
        # Get value counts
        baseline_counts = baseline.value_counts()
        current_counts = current.value_counts()
        
        # Get all unique categories
        all_categories = set(baseline_counts.index) | set(current_counts.index)
        
        # Create contingency table
        baseline_freq = [baseline_counts.get(cat, 0) for cat in all_categories]
        current_freq = [current_counts.get(cat, 0) for cat in all_categories]
        
        # Chi-square test
        contingency_table = np.array([baseline_freq, current_freq])
        chi2, pvalue, dof, expected = chi2_contingency(contingency_table)
        
        results['chi2_statistic'] = chi2
        results['chi2_pvalue'] = pvalue
        results['chi2_drift_detected'] = pvalue < KS_PVALUE_THRESHOLD
        
        # Calculate PSI for categorical
        baseline_probs = np.array(baseline_freq) / sum(baseline_freq)
        current_probs = np.array(current_freq) / sum(current_freq)
        
        # Avoid division by zero
        baseline_probs = np.where(baseline_probs == 0, 1e-10, baseline_probs)
        current_probs = np.where(current_probs == 0, 1e-10, current_probs)
        
        psi = np.sum((current_probs - baseline_probs) * 
                     np.log(current_probs / baseline_probs))
        results['psi'] = psi
        results['psi_drift_detected'] = psi > PSI_THRESHOLD_WARNING
        
        # Category distribution shift
        results['baseline_categories'] = len(baseline_counts)
        results['current_categories'] = len(current_counts)
        results['new_categories'] = len(set(current_counts.index) - set(baseline_counts.index))
        results['missing_categories'] = len(set(baseline_counts.index) - set(current_counts.index))
        
    except Exception as e:
        logger.error(f"Error in categorical drift detection: {str(e)}")
        results['error'] = str(e)
    
    return results

# COMMAND ----------

def load_baseline_data(spark: SparkSession, table_name: str, days: int = 30):
    """
    Load baseline data (reference period)
    
    Args:
        spark: SparkSession
        table_name: Delta table name
        days: Number of days to use as baseline
    
    Returns:
        Pandas DataFrame
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        baseline_df = spark.read.table(table_name).filter(
            col("created_at") >= lit(cutoff_date)
        ).toPandas()
        
        logger.info(f"Loaded {len(baseline_df)} baseline records")
        return baseline_df
    except Exception as e:
        logger.error(f"Error loading baseline data: {str(e)}")
        raise

# COMMAND ----------

def load_current_data(spark: SparkSession, table_name: str, days: int = 7):
    """
    Load current data (monitoring period)
    
    Args:
        spark: SparkSession
        table_name: Delta table name
        days: Number of recent days to monitor
    
    Returns:
        Pandas DataFrame
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        current_df = spark.read.table(table_name).filter(
            col("created_at") >= lit(cutoff_date)
        ).toPandas()
        
        logger.info(f"Loaded {len(current_df)} current records")
        return current_df
    except Exception as e:
        logger.error(f"Error loading current data: {str(e)}")
        raise

# COMMAND ----------

def detect_feature_drift(baseline_df: pd.DataFrame, current_df: pd.DataFrame, feature_columns: list):
    """
    Detect drift across all features
    
    Args:
        baseline_df: Baseline DataFrame
        current_df: Current DataFrame
        feature_columns: List of feature columns to monitor
    
    Returns:
        DataFrame with drift results
    """
    drift_results = []
    
    for feature in feature_columns:
        if feature not in baseline_df.columns or feature not in current_df.columns:
            logger.warning(f"Feature {feature} not found in dataframes")
            continue
        
        baseline_series = baseline_df[feature]
        current_series = current_df[feature]
        
        # Determine if numerical or categorical
        is_numerical = pd.api.types.is_numeric_dtype(baseline_series)
        
        if is_numerical:
            results = detect_numerical_drift(baseline_series, current_series)
        else:
            results = detect_categorical_drift(baseline_series, current_series)
        
        results['feature_name'] = feature
        results['feature_type'] = 'numerical' if is_numerical else 'categorical'
        results['baseline_count'] = len(baseline_series.dropna())
        results['current_count'] = len(current_series.dropna())
        results['detection_timestamp'] = datetime.now()
        
        drift_results.append(results)
    
    return pd.DataFrame(drift_results)

# COMMAND ----------

def save_drift_results(spark: SparkSession, drift_df: pd.DataFrame, table_name: str):
    """
    Save drift detection results to Delta table
    
    Args:
        spark: SparkSession
        drift_df: DataFrame with drift results
        table_name: Target Delta table name
    """
    try:
        spark_df = spark.createDataFrame(drift_df)
        
        spark_df.write \
            .format("delta") \
            .mode("append") \
            .option("mergeSchema", "true") \
            .saveAsTable(table_name)
        
        logger.info(f"Saved drift results to {table_name}")
    except Exception as e:
        logger.error(f"Error saving drift results: {str(e)}")
        raise

# COMMAND ----------

def send_drift_alert(drift_df: pd.DataFrame):
    """
    Send alerts when significant drift is detected
    
    Args:
        drift_df: DataFrame with drift results
    """
    try:
        # Find features with critical drift
        critical_drift = drift_df[
            (drift_df['psi'] > PSI_THRESHOLD_CRITICAL) |
            (drift_df.get('ks_drift_detected', False)) |
            (drift_df.get('chi2_drift_detected', False))
        ]
        
        if len(critical_drift) > 0:
            logger.warning("=" * 50)
            logger.warning("CRITICAL DRIFT DETECTED!")
            logger.warning("=" * 50)
            for _, row in critical_drift.iterrows():
                logger.warning(f"Feature: {row['feature_name']}")
                logger.warning(f"  PSI: {row.get('psi', 'N/A'):.4f}")
                logger.warning(f"  Drift Status: CRITICAL")
            logger.warning("=" * 50)
            
            # In production, send to Slack/Email
            # send_slack_alert(critical_drift)
            # send_email_alert(critical_drift)
        
        # Find features with warning-level drift
        warning_drift = drift_df[
            (drift_df['psi'] > PSI_THRESHOLD_WARNING) &
            (drift_df['psi'] <= PSI_THRESHOLD_CRITICAL)
        ]
        
        if len(warning_drift) > 0:
            logger.info("Warning-level drift detected:")
            for _, row in warning_drift.iterrows():
                logger.info(f"  {row['feature_name']}: PSI = {row.get('psi', 'N/A'):.4f}")
    
    except Exception as e:
        logger.error(f"Error sending alerts: {str(e)}")

# COMMAND ----------

# Main execution
if __name__ == "__main__":
    try:
        spark = SparkSession.builder.appName("DriftDetection").getOrCreate()
        
        logger.info("=" * 50)
        logger.info("Starting Drift Detection")
        logger.info("=" * 50)
        
        # Load baseline and current data
        baseline_df = load_baseline_data(spark, BASELINE_TABLE, days=30)
        current_df = load_current_data(spark, CURRENT_TABLE, days=7)
        
        # Define features to monitor
        feature_columns = [
            'company_size', 'industry', 'page_views', 'time_on_site',
            'form_completion_time', 'referral_source', 'hour_of_day',
            'day_of_week', 'engagement_score'
        ]
        
        # Detect drift
        drift_results_df = detect_feature_drift(baseline_df, current_df, feature_columns)
        
        # Save results
        save_drift_results(spark, drift_results_df, DRIFT_RESULTS_TABLE)
        
        # Send alerts
        send_drift_alert(drift_results_df)
        
        logger.info("=" * 50)
        logger.info("Drift Detection Completed")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Fatal error in drift detection: {str(e)}")
        raise

