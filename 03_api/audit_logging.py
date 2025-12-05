"""
RAKEZ Lead Scoring Model - Comprehensive Audit Logging
Production audit logging system for compliance and security

Features:
- Comprehensive action logging
- User tracking
- IP address logging
- Immutable audit trail
- Compliance reporting
"""

from datetime import datetime
from typing import Dict, Optional, List
import json
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
AUDIT_TABLE = os.getenv("AUDIT_TABLE", "default.audit_logs")
AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "2555"))  # 7 years for compliance


class AuditLogger:
    """
    Comprehensive audit logging system for compliance and security
    """
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """
        Initialize audit logger
        
        Args:
            spark: SparkSession for writing to Delta Lake (optional)
        """
        self.spark = spark
        self.audit_table = AUDIT_TABLE
        self.audit_buffer = []  # Buffer for batch writes
    
    def log_action(
        self,
        action: str,
        user: str,
        resource: str,
        details: Dict,
        ip_address: str,
        status: str = "SUCCESS",
        user_role: Optional[str] = None
    ) -> Dict:
        """
        Log a critical action to audit trail
        
        Args:
            action: Action type (PREDICTION, MODEL_DEPLOY, DATA_ACCESS, etc.)
            user: Username or user ID
            resource: Resource accessed (model_name, endpoint, table_name)
            details: Additional details as dictionary
            ip_address: IP address of requester
            status: SUCCESS or FAILED
            user_role: User role (admin, data_scientist, viewer)
        
        Returns:
            Audit record dictionary
        """
        audit_record = {
            "timestamp": datetime.now(),
            "action": action,
            "user": user,
            "user_role": user_role or "unknown",
            "resource": resource,
            "details": json.dumps(details),
            "ip_address": ip_address,
            "status": status
        }
        
        # Log to console
        logger.info(f"AUDIT: {action} by {user} ({user_role}) on {resource} - {status}")
        
        # Add to buffer
        self.audit_buffer.append(audit_record)
        
        # Write to Delta Lake if Spark available
        if self.spark is not None:
            try:
                self._write_to_delta(audit_record)
            except Exception as e:
                logger.error(f"Error writing audit log to Delta: {str(e)}")
                # Keep in buffer for retry
        
        return audit_record
    
    def _write_to_delta(self, audit_record: Dict):
        """Write audit record to Delta Lake table"""
        if self.spark is None:
            return
        
        try:
            # Create DataFrame from audit record
            audit_df = self.spark.createDataFrame([audit_record])
            
            # Write to Delta table (append mode)
            audit_df.write \
                .format("delta") \
                .mode("append") \
                .option("mergeSchema", "true") \
                .saveAsTable(self.audit_table)
            
            logger.debug(f"Audit record written to {self.audit_table}")
        except Exception as e:
            logger.error(f"Error writing to Delta table: {str(e)}")
            raise
    
    def log_prediction(
        self,
        user: str,
        lead_id: str,
        prediction: float,
        ip_address: str,
        model_version: str,
        latency_ms: float,
        user_role: Optional[str] = None
    ):
        """Log a prediction action"""
        return self.log_action(
            action="PREDICTION",
            user=user,
            resource=f"lead_{lead_id}",
            details={
                "lead_id": lead_id,
                "prediction": float(prediction),
                "model_version": model_version,
                "latency_ms": float(latency_ms)
            },
            ip_address=ip_address,
            status="SUCCESS",
            user_role=user_role
        )
    
    def log_model_deployment(
        self,
        user: str,
        model_version: str,
        stage: str,
        reason: str,
        approval: Optional[str] = None,
        ip_address: str = "system"
    ):
        """Log model deployment"""
        return self.log_action(
            action="MODEL_DEPLOY",
            user=user,
            resource=f"model_{model_version}",
            details={
                "model_version": model_version,
                "stage": stage,
                "reason": reason,
                "approval": approval
            },
            ip_address=ip_address,
            status="SUCCESS",
            user_role="admin"
        )
    
    def log_model_rollback(
        self,
        user: str,
        from_version: str,
        to_version: str,
        reason: str,
        ip_address: str = "system"
    ):
        """Log model rollback"""
        return self.log_action(
            action="MODEL_ROLLBACK",
            user=user,
            resource=f"model_{from_version}",
            details={
                "from_version": from_version,
                "to_version": to_version,
                "reason": reason
            },
            ip_address=ip_address,
            status="SUCCESS",
            user_role="admin"
        )
    
    def log_data_access(
        self,
        user: str,
        table_name: str,
        operation: str,
        record_count: int,
        ip_address: str,
        user_role: Optional[str] = None
    ):
        """Log data access"""
        return self.log_action(
            action="DATA_ACCESS",
            user=user,
            resource=table_name,
            details={
                "operation": operation,
                "record_count": record_count
            },
            ip_address=ip_address,
            status="SUCCESS",
            user_role=user_role
        )
    
    def log_failed_action(
        self,
        action: str,
        user: str,
        resource: str,
        error_message: str,
        ip_address: str,
        user_role: Optional[str] = None
    ):
        """Log a failed action"""
        return self.log_action(
            action=action,
            user=user,
            resource=resource,
            details={"error": error_message},
            ip_address=ip_address,
            status="FAILED",
            user_role=user_role
        )
    
    def query_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None
    ) -> List[Dict]:
        """
        Query audit logs for compliance reporting
        
        Args:
            start_date: Start date for query
            end_date: End date for query
            user: Filter by user
            action: Filter by action type
            resource: Filter by resource
        
        Returns:
            List of audit records
        """
        if self.spark is None:
            # Return from buffer if no Spark
            return [r for r in self.audit_buffer if self._matches_filter(r, start_date, end_date, user, action, resource)]
        
        try:
            # Read from Delta table
            df = self.spark.read.table(self.audit_table)
            
            # Apply filters
            if start_date:
                df = df.filter(col("timestamp") >= lit(start_date))
            if end_date:
                df = df.filter(col("timestamp") <= lit(end_date))
            if user:
                df = df.filter(col("user") == lit(user))
            if action:
                df = df.filter(col("action") == lit(action))
            if resource:
                df = df.filter(col("resource").contains(resource))
            
            # Convert to list of dictionaries
            records = df.collect()
            return [row.asDict() for row in records]
        except Exception as e:
            logger.error(f"Error querying audit logs: {str(e)}")
            return []
    
    def _matches_filter(
        self,
        record: Dict,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        user: Optional[str],
        action: Optional[str],
        resource: Optional[str]
    ) -> bool:
        """Check if record matches filters"""
        if start_date and record["timestamp"] < start_date:
            return False
        if end_date and record["timestamp"] > end_date:
            return False
        if user and record["user"] != user:
            return False
        if action and record["action"] != action:
            return False
        if resource and resource not in record["resource"]:
            return False
        return True
    
    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Generate compliance report for audit period
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            Compliance report dictionary
        """
        logs = self.query_audit_logs(start_date, end_date)
        
        # Aggregate statistics
        total_actions = len(logs)
        actions_by_type = {}
        actions_by_user = {}
        failed_actions = 0
        
        for log in logs:
            action_type = log["action"]
            user = log["user"]
            status = log["status"]
            
            actions_by_type[action_type] = actions_by_type.get(action_type, 0) + 1
            actions_by_user[user] = actions_by_user.get(user, 0) + 1
            
            if status == "FAILED":
                failed_actions += 1
        
        return {
            "report_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_actions": total_actions,
                "failed_actions": failed_actions,
                "success_rate": (total_actions - failed_actions) / total_actions if total_actions > 0 else 0
            },
            "actions_by_type": actions_by_type,
            "actions_by_user": actions_by_user,
            "generated_at": datetime.now().isoformat()
        }


# Global audit logger instance (initialize with Spark in production)
audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    return audit_logger

