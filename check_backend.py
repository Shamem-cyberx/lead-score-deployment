"""
Check if FastAPI backend is running
"""
import requests
import sys

def check_backend():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("[OK] Backend is running!")
            print(f"    Health: {response.json()}")
            return True
        else:
            print(f"[WARN] Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Backend is NOT running!")
        print("    Start it with: python start.py --api-only")
        print("    Or: cd 03_api && uvicorn fastapi_app:app --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"[ERROR] Could not check backend: {e}")
        return False

if __name__ == "__main__":
    check_backend()

