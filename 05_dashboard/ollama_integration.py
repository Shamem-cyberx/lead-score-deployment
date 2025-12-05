"""
Ollama Integration for Advanced Dashboard Features
Provides AI-powered insights, anomaly detection, and natural language queries
"""

import requests
import json
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta

class OllamaClient:
    """Client for interacting with Ollama LLM"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = None):
        self.base_url = base_url
        self.model = model or self._get_available_model()
        self.available = self._check_availability()
    
    def _get_available_model(self) -> str:
        """Get first available model from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    # Prefer llama2, phi, or any available model
                    for model in models:
                        model_name = model.get('name', '')
                        if 'llama2' in model_name.lower():
                            return model_name
                        if 'phi' in model_name.lower():
                            return model_name
                    # Return first available model
                    return models[0].get('name', 'llama2')
        except:
            pass
        return "llama2"  # Default fallback
    
    def _check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate_insight(self, prompt: str, context: Dict = None) -> str:
        """Generate AI insight using Ollama"""
        if not self.available:
            return "Ollama is not available. Install and start Ollama to enable AI features."
        
        try:
            full_prompt = prompt
            if context:
                # Convert pandas/numpy types to native Python types for JSON serialization
                def convert_types(obj):
                    if isinstance(obj, dict):
                        return {k: convert_types(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_types(item) for item in obj]
                    elif hasattr(obj, 'item'):  # numpy/pandas scalar
                        return obj.item()
                    elif pd.isna(obj):
                        return None
                    else:
                        return obj
                
                context_clean = convert_types(context)
                full_prompt = f"Context: {json.dumps(context_clean, indent=2, default=str)}\n\n{prompt}"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 200,  # Limit response length for faster generation
                        "temperature": 0.7
                    }
                },
                timeout=60  # Increased timeout for slower models
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated")
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error generating insight: {str(e)}"
    
    def analyze_anomaly(self, metrics_df: pd.DataFrame, anomaly_type: str) -> str:
        """Analyze anomalies in metrics using AI"""
        if metrics_df.empty:
            return "No data to analyze"
        
        latest = metrics_df.iloc[-1]
        previous = metrics_df.iloc[-2] if len(metrics_df) > 1 else latest
        
        # Convert to native Python types
        def to_dict_clean(series):
            return {k: (v.item() if hasattr(v, 'item') else (None if pd.isna(v) else v)) 
                   for k, v in series.to_dict().items()}
        
        context = {
            "anomaly_type": anomaly_type,
            "current_value": to_dict_clean(latest),
            "previous_value": to_dict_clean(previous),
            "trend": "increasing" if float(latest.get('p95_latency_ms', 0)) > float(previous.get('p95_latency_ms', 0)) else "decreasing"
        }
        
        prompt = f"""Analyze this {anomaly_type} anomaly in the lead scoring model metrics.
Provide:
1. What the anomaly indicates
2. Potential root causes
3. Recommended actions

Be concise and actionable."""
        
        return self.generate_insight(prompt, context)
    
    def explain_drift(self, drift_data: pd.DataFrame) -> str:
        """Explain data drift using AI"""
        if drift_data.empty:
            return "No drift data available"
        
        critical_features = drift_data[drift_data['psi'] > 0.5]
        warning_features = drift_data[(drift_data['psi'] > 0.25) & (drift_data['psi'] <= 0.5)]
        
        context = {
            "critical_drift": critical_features[['feature_name', 'psi']].to_dict('records') if not critical_features.empty else [],
            "warning_drift": warning_features[['feature_name', 'psi']].to_dict('records') if not warning_features.empty else [],
            "total_features": len(drift_data)
        }
        
        critical_count = len(context.get("critical_drift", []))
        warning_count = len(context.get("warning_drift", []))
        
        prompt = f"""Data drift detected:
- Critical features: {critical_count}
- Warning features: {warning_count}
- Total features: {context.get('total_features', 0)}

Briefly explain what this means and 2-3 remediation steps (1 sentence each)."""
        
        return self.generate_insight(prompt, context)
    
    def generate_recommendations(self, metrics_df: pd.DataFrame, predictions_df: pd.DataFrame) -> str:
        """Generate actionable recommendations"""
        if metrics_df.empty:
            return "No metrics available"
        
        latest = metrics_df.iloc[-1]
        # Convert pandas/numpy types to native Python types
        conversion_rate = float(latest.get('conversion_rate', 0))
        latency = float(latest.get('p95_latency_ms', 0))
        error_rate = float(latest.get('error_rate', 0))
        
        context = {
            "conversion_rate": conversion_rate,
            "latency_p95": latency,
            "error_rate": error_rate,
            "total_predictions": int(len(predictions_df)) if not predictions_df.empty else 0
        }
        
        prompt = f"""Analyze these lead scoring metrics:
- Conversion Rate: {conversion_rate:.2f}%
- P95 Latency: {latency:.0f}ms
- Error Rate: {error_rate:.2f}%
- Total Predictions: {context['total_predictions']}

Provide 3 brief recommendations (1-2 sentences each)."""
        
        return self.generate_insight(prompt, context)
    
    def answer_query(self, query: str, data_summary: Dict) -> str:
        """Answer natural language queries about the data"""
        prompt = f"""User Question: {query}

Data Summary:
{json.dumps(data_summary, indent=2)}

Provide a clear, concise answer based on the data."""
        
        return self.generate_insight(prompt)

# Global Ollama client instance
ollama_client = OllamaClient()

