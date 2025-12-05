"""
RAKEZ Lead Scoring Model - Fairness Metrics and Bias Detection
Databricks Notebook for Model Fairness Assessment

This notebook provides:
1. Demographic parity metrics
2. Equalized odds assessment
3. Bias detection across sensitive groups
4. Fairness reports
"""

# Databricks notebook source
# MAGIC %md
# MAGIC # Model Fairness Assessment and Bias Detection
# MAGIC 
# MAGIC This notebook assesses model fairness and detects bias across sensitive groups.

# COMMAND ----------

# Import libraries
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, roc_auc_score
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# COMMAND ----------

# Fairlearn is optional - install if available
try:
    from fairlearn.metrics import (
        demographic_parity_difference,
        equalized_odds_difference,
        selection_rate,
        true_positive_rate,
        false_positive_rate
    )
    FAIRLEARN_AVAILABLE = True
except ImportError:
    FAIRLEARN_AVAILABLE = False
    logger.warning("fairlearn not available. Using custom implementations.")

# COMMAND ----------

class FairnessAssessment:
    """
    Class for assessing model fairness and detecting bias
    """
    
    def __init__(self, y_true: pd.Series, y_pred: pd.Series, 
                 y_proba: Optional[pd.Series] = None,
                 sensitive_features: Optional[pd.Series] = None):
        """
        Initialize fairness assessment
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (optional)
            sensitive_features: Sensitive attribute (e.g., gender, age group)
        """
        self.y_true = y_true
        self.y_pred = y_pred
        self.y_proba = y_proba
        self.sensitive_features = sensitive_features
        
        # Fairness thresholds (industry standards)
        self.thresholds = {
            "demographic_parity": 0.1,  # 10% difference max
            "equalized_odds": 0.1,  # 10% difference max
            "selection_rate": 0.1  # 10% difference max
        }
    
    def calculate_demographic_parity(self) -> Dict:
        """
        Calculate demographic parity (equal selection rates across groups)
        
        Returns:
            Dictionary with demographic parity metrics
        """
        if self.sensitive_features is None:
            return {"error": "Sensitive features not provided"}
        
        try:
            if FAIRLEARN_AVAILABLE:
                dp_diff = demographic_parity_difference(
                    self.y_true, self.y_pred, 
                    sensitive_features=self.sensitive_features
                )
            else:
                # Custom implementation
                dp_diff = self._custom_demographic_parity()
            
            # Calculate selection rates by group
            selection_rates = {}
            for group in self.sensitive_features.unique():
                group_mask = self.sensitive_features == group
                selection_rates[group] = float(self.y_pred[group_mask].mean())
            
            return {
                "demographic_parity_difference": float(dp_diff),
                "selection_rates_by_group": selection_rates,
                "threshold": self.thresholds["demographic_parity"],
                "is_fair": abs(dp_diff) <= self.thresholds["demographic_parity"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error calculating demographic parity: {str(e)}")
            return {"error": str(e)}
    
    def calculate_equalized_odds(self) -> Dict:
        """
        Calculate equalized odds (equal TPR and FPR across groups)
        
        Returns:
            Dictionary with equalized odds metrics
        """
        if self.sensitive_features is None:
            return {"error": "Sensitive features not provided"}
        
        try:
            if FAIRLEARN_AVAILABLE:
                eo_diff = equalized_odds_difference(
                    self.y_true, self.y_pred,
                    sensitive_features=self.sensitive_features
                )
            else:
                # Custom implementation
                eo_diff = self._custom_equalized_odds()
            
            # Calculate TPR and FPR by group
            group_metrics = {}
            for group in self.sensitive_features.unique():
                group_mask = self.sensitive_features == group
                y_true_group = self.y_true[group_mask]
                y_pred_group = self.y_pred[group_mask]
                
                tn, fp, fn, tp = confusion_matrix(y_true_group, y_pred_group).ravel()
                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
                fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
                
                group_metrics[group] = {
                    "true_positive_rate": float(tpr),
                    "false_positive_rate": float(fpr)
                }
            
            return {
                "equalized_odds_difference": float(eo_diff),
                "metrics_by_group": group_metrics,
                "threshold": self.thresholds["equalized_odds"],
                "is_fair": abs(eo_diff) <= self.thresholds["equalized_odds"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error calculating equalized odds: {str(e)}")
            return {"error": str(e)}
    
    def _custom_demographic_parity(self) -> float:
        """Custom implementation of demographic parity difference"""
        selection_rates = []
        for group in self.sensitive_features.unique():
            group_mask = self.sensitive_features == group
            selection_rates.append(self.y_pred[group_mask].mean())
        return float(max(selection_rates) - min(selection_rates))
    
    def _custom_equalized_odds(self) -> float:
        """Custom implementation of equalized odds difference"""
        tpr_diffs = []
        fpr_diffs = []
        
        for group in self.sensitive_features.unique():
            group_mask = self.sensitive_features == group
            y_true_group = self.y_true[group_mask]
            y_pred_group = self.y_pred[group_mask]
            
            tn, fp, fn, tp = confusion_matrix(y_true_group, y_pred_group).ravel()
            tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
            
            tpr_diffs.append(tpr)
            fpr_diffs.append(fpr)
        
        tpr_diff = max(tpr_diffs) - min(tpr_diffs)
        fpr_diff = max(fpr_diffs) - min(fpr_diffs)
        return float(max(tpr_diff, fpr_diff))
    
    def detect_bias(self) -> Dict:
        """
        Detect bias in the model
        
        Returns:
            Dictionary with bias detection results
        """
        if self.sensitive_features is None:
            return {"error": "Sensitive features not provided"}
        
        bias_issues = []
        
        # Check demographic parity
        dp_result = self.calculate_demographic_parity()
        if not dp_result.get("is_fair", True):
            bias_issues.append({
                "type": "demographic_parity",
                "severity": "high" if abs(dp_result["demographic_parity_difference"]) > 0.2 else "medium",
                "message": f"Demographic parity violation: {dp_result['demographic_parity_difference']:.3f}",
                "details": dp_result
            })
        
        # Check equalized odds
        eo_result = self.calculate_equalized_odds()
        if not eo_result.get("is_fair", True):
            bias_issues.append({
                "type": "equalized_odds",
                "severity": "high" if abs(eo_result["equalized_odds_difference"]) > 0.2 else "medium",
                "message": f"Equalized odds violation: {eo_result['equalized_odds_difference']:.3f}",
                "details": eo_result
            })
        
        return {
            "bias_detected": len(bias_issues) > 0,
            "bias_issues": bias_issues,
            "overall_fairness": "fair" if len(bias_issues) == 0 else "unfair",
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_fairness_report(self) -> Dict:
        """
        Generate comprehensive fairness report
        
        Returns:
            Dictionary with complete fairness assessment
        """
        report = {
            "assessment_date": datetime.now().isoformat(),
            "demographic_parity": self.calculate_demographic_parity(),
            "equalized_odds": self.calculate_equalized_odds(),
            "bias_detection": self.detect_bias(),
            "overall_assessment": "pending"
        }
        
        # Determine overall assessment
        dp_fair = report["demographic_parity"].get("is_fair", False)
        eo_fair = report["equalized_odds"].get("is_fair", False)
        bias_detected = report["bias_detection"].get("bias_detected", False)
        
        if dp_fair and eo_fair and not bias_detected:
            report["overall_assessment"] = "fair"
        elif not bias_detected:
            report["overall_assessment"] = "mostly_fair"
        else:
            report["overall_assessment"] = "unfair"
        
        return report

# COMMAND ----------

# Example usage
if __name__ == "__main__":
    # Example data
    # y_true = pd.Series([0, 1, 1, 0, 1, 0, 1, 1])
    # y_pred = pd.Series([0, 1, 1, 0, 0, 0, 1, 1])
    # sensitive_features = pd.Series(['A', 'A', 'B', 'B', 'A', 'B', 'A', 'B'])
    
    # Initialize fairness assessment
    # fairness = FairnessAssessment(y_true, y_pred, sensitive_features=sensitive_features)
    
    # Generate report
    # report = fairness.generate_fairness_report()
    # print(json.dumps(report, indent=2))

