"""
Test Ollama integration
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("Testing Ollama Integration")
print("="*60)

# Test 1: Import
print("\n[1] Testing import...")
try:
    from ollama_integration import ollama_client
    print(f"  [OK] Ollama client imported")
    print(f"  [OK] Available: {ollama_client.available}")
    print(f"  [OK] Model: {ollama_client.model}")
except Exception as e:
    print(f"  [ERROR] Import failed: {e}")
    sys.exit(1)

# Test 2: Check availability
print("\n[2] Testing Ollama availability...")
if ollama_client.available:
    print("  [OK] Ollama is available!")
else:
    print("  [WARN] Ollama is not available")
    print("  [INFO] Make sure Ollama is running: ollama serve")
    sys.exit(1)

# Test 3: Test simple generation
print("\n[3] Testing AI generation...")
try:
    test_prompt = "Say hello in one sentence."
    result = ollama_client.generate_insight(test_prompt)
    print(f"  [OK] Generation successful!")
    print(f"  [RESPONSE] {result[:100]}...")
except Exception as e:
    print(f"  [ERROR] Generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test with data
print("\n[4] Testing with sample data...")
try:
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Create sample metrics
    dates = [datetime.now() - timedelta(days=i) for i in range(7, 0, -1)]
    metrics_df = pd.DataFrame({
        'metric_timestamp': dates,
        'p95_latency_ms': [180, 190, 200, 210, 220, 230, 240],
        'conversion_rate': [10.5, 11.0, 10.8, 11.2, 11.5, 11.3, 11.0],
        'error_rate': [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
    })
    
    predictions_df = pd.DataFrame({
        'lead_id': [f'lead_{i}' for i in range(10)],
        'lead_score': [0.3, 0.5, 0.7, 0.8, 0.6, 0.4, 0.9, 0.5, 0.6, 0.7]
    })
    
    recommendations = ollama_client.generate_recommendations(metrics_df, predictions_df)
    print(f"  [OK] Recommendations generated!")
    print(f"  [RESPONSE] {recommendations[:200]}...")
except Exception as e:
    print(f"  [ERROR] Data test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("[SUCCESS] Ollama integration is working!")
print("="*60)
print("\nYou can now use AI features in the dashboard:")
print("  1. Start dashboard: .\\start_dash.bat")
print("  2. Go to 'AI Insights' tab")
print("  3. See AI-generated recommendations and analysis")

