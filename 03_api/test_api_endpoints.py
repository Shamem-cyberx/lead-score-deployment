"""
Test FastAPI endpoints
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("\n[1] Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Status: {data.get('status')}")
            print(f"  [OK] Model loaded: {data.get('model_loaded')}")
            return True
        else:
            print(f"  [ERROR] Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  [ERROR] Backend is not running!")
        print("  Start it with: python -m uvicorn fastapi_app:app --host 127.0.0.1 --port 8000")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_score_lead():
    """Test score-lead endpoint"""
    print("\n[2] Testing /score-lead endpoint...")
    test_data = {
        "lead_id": "test_001",
        "company_size": "Medium",
        "industry": "Technology",
        "page_views": 20,
        "time_on_site": 350.5,
        "form_completion_time": 42.3,
        "referral_source": "Google"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/score-lead",
            json=test_data,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Lead ID: {data.get('lead_id')}")
            print(f"  [OK] Score: {data.get('lead_score'):.3f}")
            print(f"  [OK] Category: {data.get('score_category')}")
            return True
        else:
            print(f"  [ERROR] Status code: {response.status_code}")
            print(f"  [ERROR] Response: {response.text}")
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_docs():
    """Test docs endpoint"""
    print("\n[3] Testing /docs endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("  [OK] API docs available at http://127.0.0.1:8000/docs")
            return True
        else:
            print(f"  [WARN] Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Testing FastAPI Backend Endpoints")
    print("="*60)
    
    # Wait a bit for server to start
    print("\nWaiting for backend to be ready...")
    time.sleep(2)
    
    results = []
    results.append(test_health())
    results.append(test_score_lead())
    results.append(test_docs())
    
    print("\n" + "="*60)
    if all(results):
        print("[SUCCESS] All tests passed!")
    else:
        print("[WARNING] Some tests failed. Check backend is running.")
    print("="*60)

