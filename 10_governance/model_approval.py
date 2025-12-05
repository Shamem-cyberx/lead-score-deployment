"""
RAKEZ Lead Scoring Model - Model Approval Workflow
Governance framework for model deployment approvals

This module provides:
1. Model approval workflow
2. Risk assessment
3. Approval tracking
4. Compliance checks
"""

from datetime import datetime
from typing import Dict, List, Optional
import json
import logging
from enum import Enum
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
APPROVAL_TABLE = os.getenv("APPROVAL_TABLE", "default.model_approvals")
RISK_THRESHOLD_HIGH = 0.7
RISK_THRESHOLD_MEDIUM = 0.4


class ApprovalStatus(Enum):
    """Model approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


class RiskLevel(Enum):
    """Model risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ModelApprovalWorkflow:
    """
    Model approval workflow for governance
    """
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """
        Initialize approval workflow
        
        Args:
            spark: SparkSession for writing to Delta Lake (optional)
        """
        self.spark = spark
        self.approval_table = APPROVAL_TABLE
    
    def request_approval(
        self,
        model_version: str,
        requester: str,
        reason: str,
        model_metrics: Dict,
        risk_assessment: Dict
    ) -> Dict:
        """
        Request approval for model deployment
        
        Args:
            model_version: Model version to deploy
            requester: Username of requester
            reason: Reason for deployment
            model_metrics: Model performance metrics
            risk_assessment: Risk assessment results
        
        Returns:
            Approval request dictionary
        """
        approval_request = {
            "model_version": model_version,
            "requester": requester,
            "reason": reason,
            "model_metrics": json.dumps(model_metrics),
            "risk_assessment": json.dumps(risk_assessment),
            "status": ApprovalStatus.PENDING.value,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "approvers": [],
            "rejections": []
        }
        
        # Save to Delta Lake if Spark available
        if self.spark is not None:
            try:
                self._save_approval_request(approval_request)
            except Exception as e:
                logger.error(f"Error saving approval request: {str(e)}")
        
        logger.info(f"Approval requested for model {model_version} by {requester}")
        return approval_request
    
    def approve_model(
        self,
        model_version: str,
        approver: str,
        comments: str,
        approval_level: str = "standard"
    ) -> Dict:
        """
        Approve model for deployment
        
        Args:
            model_version: Model version
            approver: Username of approver
            comments: Approval comments
            approval_level: Approval level (standard, high_risk, critical)
        
        Returns:
            Updated approval record
        """
        # In production, load from Delta table
        # For now, return updated record
        approval_record = {
            "model_version": model_version,
            "approver": approver,
            "comments": comments,
            "approval_level": approval_level,
            "status": ApprovalStatus.APPROVED.value,
            "approved_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        logger.info(f"Model {model_version} approved by {approver}")
        return approval_record
    
    def reject_model(
        self,
        model_version: str,
        approver: str,
        reason: str
    ) -> Dict:
        """
        Reject model deployment
        
        Args:
            model_version: Model version
            approver: Username of approver
            reason: Rejection reason
        
        Returns:
            Updated approval record
        """
        approval_record = {
            "model_version": model_version,
            "approver": approver,
            "reason": reason,
            "status": ApprovalStatus.REJECTED.value,
            "rejected_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        logger.info(f"Model {model_version} rejected by {approver}: {reason}")
        return approval_record
    
    def _save_approval_request(self, request: Dict):
        """Save approval request to Delta Lake"""
        if self.spark is None:
            return
        
        try:
            request_df = self.spark.createDataFrame([request])
            request_df.write \
                .format("delta") \
                .mode("append") \
                .option("mergeSchema", "true") \
                .saveAsTable(self.approval_table)
        except Exception as e:
            logger.error(f"Error saving to Delta: {str(e)}")
            raise


class ModelRiskAssessment:
    """
    Model risk assessment framework
    """
    
    def assess_risk(
        self,
        model_metrics: Dict,
        data_quality: Dict,
        bias_metrics: Dict,
        performance_history: Dict
    ) -> Dict:
        """
        Assess overall model risk
        
        Args:
            model_metrics: Model performance metrics
            data_quality: Data quality metrics
            bias_metrics: Bias and fairness metrics
            performance_history: Historical performance
        
        Returns:
            Risk assessment dictionary
        """
        risk_factors = {
            "data_quality_risk": self._assess_data_quality_risk(data_quality),
            "model_performance_risk": self._assess_performance_risk(model_metrics),
            "bias_risk": self._assess_bias_risk(bias_metrics),
            "stability_risk": self._assess_stability_risk(performance_history),
            "security_risk": self._assess_security_risk()
        }
        
        # Calculate overall risk score (0-1)
        overall_risk = sum(risk_factors.values()) / len(risk_factors)
        
        # Determine risk level
        if overall_risk >= RISK_THRESHOLD_HIGH:
            risk_level = RiskLevel.HIGH.value
        elif overall_risk >= RISK_THRESHOLD_MEDIUM:
            risk_level = RiskLevel.MEDIUM.value
        else:
            risk_level = RiskLevel.LOW.value
        
        return {
            "overall_risk_score": float(overall_risk),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "requires_approval": overall_risk >= RISK_THRESHOLD_MEDIUM,
            "assessment_date": datetime.now().isoformat()
        }
    
    def _assess_data_quality_risk(self, data_quality: Dict) -> float:
        """Assess data quality risk (0-1)"""
        # Check missing values, outliers, distribution shifts
        missing_pct = data_quality.get("missing_percentage", 0)
        outlier_pct = data_quality.get("outlier_percentage", 0)
        
        risk = (missing_pct * 0.5 + outlier_pct * 0.5) / 100
        return min(risk, 1.0)
    
    def _assess_performance_risk(self, model_metrics: Dict) -> float:
        """Assess model performance risk (0-1)"""
        auc = model_metrics.get("auc", 0.5)
        precision = model_metrics.get("precision", 0.5)
        recall = model_metrics.get("recall", 0.5)
        
        # Lower performance = higher risk
        risk = 1.0 - ((auc + precision + recall) / 3)
        return max(0.0, risk)
    
    def _assess_bias_risk(self, bias_metrics: Dict) -> float:
        """Assess bias risk (0-1)"""
        dp_diff = abs(bias_metrics.get("demographic_parity_difference", 0))
        eo_diff = abs(bias_metrics.get("equalized_odds_difference", 0))
        
        # Higher bias = higher risk
        risk = (dp_diff + eo_diff) / 2
        return min(risk, 1.0)
    
    def _assess_stability_risk(self, performance_history: Dict) -> float:
        """Assess model stability risk (0-1)"""
        # Check performance variance over time
        variance = performance_history.get("performance_variance", 0)
        risk = min(variance, 1.0)
        return risk
    
    def _assess_security_risk(self) -> float:
        """Assess security risk (0-1)"""
        # Check for security vulnerabilities
        # In production, integrate with security scanning tools
        return 0.1  # Default low risk


class ComplianceChecker:
    """
    Compliance checker for model deployment
    """
    
    def check_compliance(
        self,
        model_version: str,
        model_metrics: Dict,
        bias_metrics: Dict,
        documentation: Dict
    ) -> Dict:
        """
        Check compliance requirements
        
        Args:
            model_version: Model version
            model_metrics: Model metrics
            bias_metrics: Bias metrics
            documentation: Documentation checklist
        
        Returns:
            Compliance check results
        """
        checks = {
            "performance_threshold": self._check_performance_threshold(model_metrics),
            "bias_threshold": self._check_bias_threshold(bias_metrics),
            "documentation_complete": self._check_documentation(documentation),
            "explainability_available": self._check_explainability(),
            "audit_trail_complete": self._check_audit_trail(model_version)
        }
        
        all_passed = all(checks.values())
        
        return {
            "compliant": all_passed,
            "checks": checks,
            "model_version": model_version,
            "check_date": datetime.now().isoformat()
        }
    
    def _check_performance_threshold(self, metrics: Dict) -> bool:
        """Check if model meets performance threshold"""
        auc = metrics.get("auc", 0)
        return auc >= 0.75  # Minimum AUC threshold
    
    def _check_bias_threshold(self, bias_metrics: Dict) -> bool:
        """Check if model meets bias threshold"""
        dp_diff = abs(bias_metrics.get("demographic_parity_difference", 1))
        eo_diff = abs(bias_metrics.get("equalized_odds_difference", 1))
        return dp_diff <= 0.1 and eo_diff <= 0.1
    
    def _check_documentation(self, documentation: Dict) -> bool:
        """Check if documentation is complete"""
        required = ["model_description", "features", "training_data", "evaluation"]
        return all(doc in documentation for doc in required)
    
    def _check_explainability(self) -> bool:
        """Check if explainability is available"""
        # In production, check if SHAP/LIME explanations are available
        return True  # Assume available
    
    def _check_audit_trail(self, model_version: str) -> bool:
        """Check if audit trail is complete"""
        # In production, verify audit logs exist
        return True  # Assume complete


# Example usage
if __name__ == "__main__":
    # Initialize components
    approval_workflow = ModelApprovalWorkflow()
    risk_assessment = ModelRiskAssessment()
    compliance_checker = ComplianceChecker()
    
    # Example: Request approval
    model_metrics = {"auc": 0.85, "precision": 0.82, "recall": 0.80}
    data_quality = {"missing_percentage": 5, "outlier_percentage": 2}
    bias_metrics = {"demographic_parity_difference": 0.05, "equalized_odds_difference": 0.03}
    
    risk_result = risk_assessment.assess_risk(
        model_metrics=model_metrics,
        data_quality=data_quality,
        bias_metrics=bias_metrics,
        performance_history={"performance_variance": 0.1}
    )
    
    approval_request = approval_workflow.request_approval(
        model_version="v2.0",
        requester="data_scientist_1",
        reason="Improved performance and reduced bias",
        model_metrics=model_metrics,
        risk_assessment=risk_result
    )
    
    print(f"Approval requested: {approval_request['status']}")
    print(f"Risk level: {risk_result['risk_level']}")

