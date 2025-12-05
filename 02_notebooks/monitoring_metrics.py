"""
RAKEZ Lead Scoring Model - Monitoring Metrics
Databricks Notebook for Real-time Performance Monitoring

This notebook:
1. Calculates latency metrics (P50, P95, P99)
2. Tracks throughput (requests per second)
3. Monitors conversion rates
4. Logs metrics to Delta tables
"""

# Databricks notebook source
# MAGIC %md
# MAGIC # Model Performance Monitoring
# MAGIC 
# MAGIC This notebook tracks key performance metrics for the lead scoring model.

# COMMAND ----------

# Import libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp, avg, count, percentile_approx
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, IntegerType
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# COMMAND ----------

# Configuration
API_LOGS_TABLE = "default.api_request_logs"
PREDICTIONS_TABLE = "default.lead_predictions"
METRICS_TABLE = "default.monitoring_metrics"
CONVERSION_TABLE = "default.lead_conversions"

# Latency thresholds (milliseconds)
LATENCY_P95_WARNING = 200
LATENCY_P95_CRITICAL = 500
THROUGHPUT_MIN = 10  # requests per second

# COMMAND ----------

def calculate_latency_metrics(spark: SparkSession, table_name: str, hours: int = 24):
    """
    Calculate latency percentiles from API logs
    
    Args:
        spark: SparkSession
        table_name: Delta table with API logs
        hours: Time window in hours
    
    Returns:
        Dictionary with latency metrics
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Load API logs
        logs_df = spark.read.table(table_name).filter(
            col("timestamp") >= lit(cutoff_time)
        )
        
        if logs_df.count() == 0:
            logger.warning("No API logs found for latency calculation")
            return {
                'p50_latency_ms': 0,
                'p95_latency_ms': 0,
                'p99_latency_ms': 0,
                'mean_latency_ms': 0,
                'max_latency_ms': 0,
                'min_latency_ms': 0,
                'request_count': 0
            }
        
        # Calculate percentiles
        latency_stats = logs_df.select(
            percentile_approx("latency_ms", 0.50).alias("p50"),
            percentile_approx("latency_ms", 0.95).alias("p95"),
            percentile_approx("latency_ms", 0.99).alias("p99"),
            avg("latency_ms").alias("mean"),
            count("*").alias("count")
        ).collect()[0]
        
        # Get min and max
        min_max = logs_df.agg(
            {"latency_ms": "min", "latency_ms": "max"}
        ).collect()[0]
        
        metrics = {
            'p50_latency_ms': latency_stats['p50'] or 0,
            'p95_latency_ms': latency_stats['p95'] or 0,
            'p99_latency_ms': latency_stats['p99'] or 0,
            'mean_latency_ms': latency_stats['mean'] or 0,
            'min_latency_ms': min_max['min(latency_ms)'] or 0,
            'max_latency_ms': min_max['max(latency_ms)'] or 0,
            'request_count': latency_stats['count'] or 0
        }
        
        logger.info(f"Latency metrics calculated: P95 = {metrics['p95_latency_ms']:.2f}ms")
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating latency metrics: {str(e)}")
        raise

# COMMAND ----------

def calculate_throughput(spark: SparkSession, table_name: str, hours: int = 1):
    """
    Calculate throughput (requests per second)
    
    Args:
        spark: SparkSession
        table_name: Delta table with API logs
        hours: Time window in hours
    
    Returns:
        Dictionary with throughput metrics
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Load API logs
        logs_df = spark.read.table(table_name).filter(
            col("timestamp") >= lit(cutoff_time)
        )
        
        request_count = logs_df.count()
        
        if request_count == 0:
            return {
                'requests_per_second': 0,
                'requests_per_minute': 0,
                'total_requests': 0,
                'time_window_hours': hours
            }
        
        # Calculate requests per second
        time_window_seconds = hours * 3600
        requests_per_second = request_count / time_window_seconds
        requests_per_minute = request_count / (hours * 60)
        
        metrics = {
            'requests_per_second': requests_per_second,
            'requests_per_minute': requests_per_minute,
            'total_requests': request_count,
            'time_window_hours': hours
        }
        
        logger.info(f"Throughput: {requests_per_second:.2f} requests/second")
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating throughput: {str(e)}")
        raise

# COMMAND ----------

def calculate_conversion_rate(spark: SparkSession, predictions_table: str, 
                             conversions_table: str, days: int = 30):
    """
    Calculate conversion rate (leads → customers)
    
    Args:
        spark: SparkSession
        predictions_table: Table with lead predictions
        conversions_table: Table with conversion events
        days: Time window in days
    
    Returns:
        Dictionary with conversion metrics
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Load predictions
        predictions_df = spark.read.table(predictions_table).filter(
            col("prediction_timestamp") >= lit(cutoff_date)
        )
        
        # Load conversions
        conversions_df = spark.read.table(conversions_table).filter(
            col("conversion_date") >= lit(cutoff_date)
        )
        
        total_leads = predictions_df.count()
        total_conversions = conversions_df.count()
        
        if total_leads == 0:
            return {
                'conversion_rate': 0.0,
                'total_leads': 0,
                'total_conversions': 0,
                'conversion_rate_by_score_bucket': {}
            }
        
        conversion_rate = (total_conversions / total_leads) * 100
        
        # Calculate conversion rate by score bucket
        predictions_pd = predictions_df.select("lead_id", "lead_score").toPandas()
        conversions_pd = conversions_df.select("lead_id").toPandas()
        
        # Merge to find converted leads
        merged = predictions_pd.merge(
            conversions_pd, on="lead_id", how="left", indicator=True
        )
        merged['converted'] = (merged['_merge'] == 'both').astype(int)
        
        # Bucket scores
        merged['score_bucket'] = pd.cut(
            merged['lead_score'], 
            bins=[0, 0.3, 0.5, 0.7, 1.0],
            labels=['Low (0-0.3)', 'Medium (0.3-0.5)', 'High (0.5-0.7)', 'Very High (0.7-1.0)']
        )
        
        conversion_by_bucket = merged.groupby('score_bucket').agg({
            'converted': ['sum', 'count']
        }).reset_index()
        conversion_by_bucket.columns = ['score_bucket', 'conversions', 'total']
        conversion_by_bucket['conversion_rate'] = (
            conversion_by_bucket['conversions'] / conversion_by_bucket['total'] * 100
        )
        
        bucket_dict = dict(zip(
            conversion_by_bucket['score_bucket'],
            conversion_by_bucket['conversion_rate']
        ))
        
        metrics = {
            'conversion_rate': conversion_rate,
            'total_leads': total_leads,
            'total_conversions': total_conversions,
            'conversion_rate_by_score_bucket': bucket_dict
        }
        
        logger.info(f"Conversion rate: {conversion_rate:.2f}%")
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating conversion rate: {str(e)}")
        raise

# COMMAND ----------

def calculate_error_rate(spark: SparkSession, table_name: str, hours: int = 24):
    """
    Calculate error rate from API logs
    
    Args:
        spark: SparkSession
        table_name: Delta table with API logs
        hours: Time window in hours
    
    Returns:
        Dictionary with error metrics
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        logs_df = spark.read.table(table_name).filter(
            col("timestamp") >= lit(cutoff_time)
        )
        
        total_requests = logs_df.count()
        
        if total_requests == 0:
            return {
                'error_rate': 0.0,
                'total_requests': 0,
                'error_count': 0,
                'success_count': 0
            }
        
        error_count = logs_df.filter(col("status_code") >= 400).count()
        success_count = total_requests - error_count
        
        error_rate = (error_count / total_requests) * 100
        
        metrics = {
            'error_rate': error_rate,
            'total_requests': total_requests,
            'error_count': error_count,
            'success_count': success_count
        }
        
        logger.info(f"Error rate: {error_rate:.2f}%")
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating error rate: {str(e)}")
        raise

# COMMAND ----------

def calculate_model_performance_metrics(spark: SparkSession, predictions_table: str, 
                                        conversions_table: str, days: int = 30):
    """
    Calculate model performance metrics (precision, recall, etc.)
    
    Args:
        spark: SparkSession
        predictions_table: Table with predictions
        conversions_table: Table with actual conversions
        days: Time window in days
    
    Returns:
        Dictionary with performance metrics
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Load predictions and conversions
        predictions_df = spark.read.table(predictions_table).filter(
            col("prediction_timestamp") >= lit(cutoff_date)
        )
        
        conversions_df = spark.read.table(conversions_table).filter(
            col("conversion_date") >= lit(cutoff_date)
        )
        
        # Convert to Pandas for easier calculation
        pred_pd = predictions_df.select("lead_id", "lead_score").toPandas()
        conv_pd = conversions_df.select("lead_id").toPandas()
        
        # Merge
        merged = pred_pd.merge(
            conv_pd, on="lead_id", how="left", indicator=True
        )
        merged['actual'] = (merged['_merge'] == 'both').astype(int)
        merged['predicted'] = (merged['lead_score'] >= 0.5).astype(int)
        
        # Calculate metrics
        tp = ((merged['predicted'] == 1) & (merged['actual'] == 1)).sum()
        fp = ((merged['predicted'] == 1) & (merged['actual'] == 0)).sum()
        tn = ((merged['predicted'] == 0) & (merged['actual'] == 0)).sum()
        fn = ((merged['predicted'] == 0) & (merged['actual'] == 1)).sum()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        accuracy = (tp + tn) / len(merged) if len(merged) > 0 else 0
        
        metrics = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'accuracy': accuracy,
            'true_positives': int(tp),
            'false_positives': int(fp),
            'true_negatives': int(tn),
            'false_negatives': int(fn)
        }
        
        logger.info(f"Model Performance - Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1_score:.4f}")
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating model performance metrics: {str(e)}")
        raise

# COMMAND ----------

def save_metrics(spark: SparkSession, metrics_dict: dict, table_name: str):
    """
    Save monitoring metrics to Delta table
    
    Args:
        spark: SparkSession
        metrics_dict: Dictionary with metrics
        table_name: Target Delta table name
    """
    try:
        # Add timestamp
        metrics_dict['metric_timestamp'] = datetime.now()
        
        # Convert to DataFrame
        metrics_df = pd.DataFrame([metrics_dict])
        spark_df = spark.createDataFrame(metrics_df)
        
        # Save to Delta table
        spark_df.write \
            .format("delta") \
            .mode("append") \
            .option("mergeSchema", "true") \
            .saveAsTable(table_name)
        
        logger.info(f"Saved metrics to {table_name}")
    except Exception as e:
        logger.error(f"Error saving metrics: {str(e)}")
        raise

# COMMAND ----------

def check_alert_thresholds(metrics: dict):
    """
    Check if metrics exceed alert thresholds
    
    Args:
        metrics: Dictionary with metrics
    """
    alerts = []
    
    # Latency alerts
    if metrics.get('p95_latency_ms', 0) > LATENCY_P95_CRITICAL:
        alerts.append({
            'level': 'CRITICAL',
            'metric': 'Latency P95',
            'value': metrics['p95_latency_ms'],
            'threshold': LATENCY_P95_CRITICAL
        })
    elif metrics.get('p95_latency_ms', 0) > LATENCY_P95_WARNING:
        alerts.append({
            'level': 'WARNING',
            'metric': 'Latency P95',
            'value': metrics['p95_latency_ms'],
            'threshold': LATENCY_P95_WARNING
        })
    
    # Throughput alerts
    if metrics.get('requests_per_second', 0) < THROUGHPUT_MIN:
        alerts.append({
            'level': 'WARNING',
            'metric': 'Throughput',
            'value': metrics['requests_per_second'],
            'threshold': THROUGHPUT_MIN
        })
    
    # Error rate alerts
    if metrics.get('error_rate', 0) > 1.0:
        alerts.append({
            'level': 'CRITICAL',
            'metric': 'Error Rate',
            'value': metrics['error_rate'],
            'threshold': 1.0
        })
    
    if alerts:
        logger.warning("=" * 50)
        logger.warning("ALERTS TRIGGERED:")
        for alert in alerts:
            logger.warning(f"{alert['level']}: {alert['metric']} = {alert['value']:.2f} (threshold: {alert['threshold']})")
        logger.warning("=" * 50)
        # In production: send_slack_alert(alerts)
    
    return alerts

# COMMAND ----------

# Main execution
if __name__ == "__main__":
    try:
        spark = SparkSession.builder.appName("MonitoringMetrics").getOrCreate()
        
        logger.info("=" * 50)
        logger.info("Starting Metrics Monitoring")
        logger.info("=" * 50)
        
        # Calculate all metrics
        latency_metrics = calculate_latency_metrics(spark, API_LOGS_TABLE, hours=24)
        throughput_metrics = calculate_throughput(spark, API_LOGS_TABLE, hours=1)
        conversion_metrics = calculate_conversion_rate(spark, PREDICTIONS_TABLE, CONVERSION_TABLE, days=30)
        error_metrics = calculate_error_rate(spark, API_LOGS_TABLE, hours=24)
        performance_metrics = calculate_model_performance_metrics(spark, PREDICTIONS_TABLE, CONVERSION_TABLE, days=30)
        
        # Combine all metrics
        all_metrics = {
            **latency_metrics,
            **throughput_metrics,
            **conversion_metrics,
            **error_metrics,
            **performance_metrics
        }
        
        # Save metrics
        save_metrics(spark, all_metrics, METRICS_TABLE)
        
        # Check alerts
        check_alert_thresholds(all_metrics)
        
        logger.info("=" * 50)
        logger.info("Metrics Monitoring Completed")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Fatal error in metrics monitoring: {str(e)}")
        raise

