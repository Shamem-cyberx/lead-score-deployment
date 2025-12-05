"""
Test explainability endpoint - checks if server is running first
Run this AFTER starting the server in another terminal
"""

import requests
import json
import sys
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_explain():
    """Test explainability endpoint"""
    
    print("="*70)
    print("Testing Explainability Endpoint")
    print("="*70)
    print()
    
    # Check server
    print("1. Checking if server is running...")
    if not check_server():
        print("   ❌ Server is NOT running!")
        print()
        print("   📋 Please start the server FIRST:")
        print("      Option 1: Double-click 'start_server.bat'")
        print("      Option 2: Run: python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000")
        print()
        print("   Then run this test script again in a NEW terminal.")
        sys.exit(1)
    
    print("   ✅ Server is running!")
    print()
    
    # Test data
    test_data = {
        "lead_id": "test_001",
        "company_size": "Medium",
        "industry": "Technology",
        "page_views": 15,
        "time_on_site": 450.5,
        "form_completion_time": 120.0,
        "referral_source": "Organic Search",
        "created_at": datetime.now().isoformat()
    }
    
    # Test SHAP
    print("2. Testing /explain-prediction with SHAP method...")
    print(f"   URL: {API_URL}/explain-prediction?method=shap")
    print()
    
    try:
        response = requests.post(
            f"{API_URL}/explain-prediction?method=shap",
            json=test_data,
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ SUCCESS!")
            print()
            print("   📊 Explanation Results:")
            print(f"      Lead ID: {result.get('lead_id')}")
            print(f"      Prediction: {result.get('prediction'):.4f}")
            print(f"      Method: {result.get('explanation_method')}")
            print(f"      Base Value: {result.get('base_value', 'N/A')}")
            print()
            print("   🔍 Feature Contributions (Top 10):")
            contributions = result.get('feature_contributions', {})
            sorted_features = sorted(
                contributions.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:10]
            
            for i, (feature, value) in enumerate(sorted_features, 1):
                sign = "+" if value >= 0 else ""
                print(f"      {i:2d}. {feature:25s}: {sign}{value:+.4f}")
            
            print()
            print("="*70)
            print("✅ Test completed successfully!")
            print("="*70)
            return True
            
        elif response.status_code == 503:
            print("   ⚠️  Model not loaded!")
            print("   Run: python create_dummy_model.py")
            return False
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to server!")
        print("   Make sure the server is running.")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False
    
    # Test LIME
    print()
    print("3. Testing /explain-prediction with LIME method...")
    try:
        response = requests.post(
            f"{API_URL}/explain-prediction?method=lime",
            json=test_data,
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ SUCCESS! Method: {result.get('explanation_method')}")
        else:
            print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Error: {str(e)}")

if __name__ == "__main__":
    success = test_explain()
    if not success:
        sys.exit(1)

