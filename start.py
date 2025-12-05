"""
RAKEZ Lead Scoring - Start Script
Quick launcher for all services
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def print_banner():
    """Print startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║     RAKEZ Lead Scoring Model - Production System            ║
    ║     Starting Services...                                     ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n[1/4] Checking dependencies...")
    required = ['fastapi', 'uvicorn', 'streamlit', 'mlflow', 'pandas', 'numpy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            missing.append(package)
            print(f"  ✗ {package} - MISSING")
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    return True

def check_model():
    """Check if model is registered in MLflow"""
    print("\n[2/4] Checking MLflow model...")
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        
        client = MlflowClient()
        try:
            versions = client.get_latest_versions("lead_scoring_model", stages=["Production"])
            if versions:
                print(f"  ✓ Model found: lead_scoring_model (Version {versions[0].version})")
                return True
            else:
                print("  ⚠️  Model not in Production stage")
                print("     Run: python 03_api/create_dummy_model.py")
                return False
        except:
            print("  ⚠️  Model not registered")
            print("     Run: python 03_api/create_dummy_model.py")
            return False
    except Exception as e:
        print(f"  ⚠️  Could not check model: {e}")
        return False

def start_fastapi(port=8000):
    """Start FastAPI server"""
    print(f"\n[3/4] Starting FastAPI server on port {port}...")
    api_dir = Path(__file__).parent / "03_api"
    
    if not api_dir.exists():
        print("  ✗ API directory not found")
        return None
    
    os.chdir(api_dir)
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "fastapi_app:app", 
         "--host", "0.0.0.0", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print(f"  ✓ FastAPI server starting...")
    print(f"     API Docs: http://localhost:{port}/docs")
    print(f"     Health: http://localhost:{port}/health")
    return process

def start_dashboard(port=8501):
    """Start Streamlit dashboard"""
    print(f"\n[4/4] Starting Streamlit dashboard on port {port}...")
    dashboard_dir = Path(__file__).parent / "05_dashboard"
    
    if not dashboard_dir.exists():
        print("  ✗ Dashboard directory not found")
        return None
    
    os.chdir(dashboard_dir)
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "streamlit_dashboard.py",
         "--server.port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print(f"  ✓ Dashboard starting...")
    print(f"     URL: http://localhost:{port}")
    return process

def main():
    parser = argparse.ArgumentParser(description="Start RAKEZ Lead Scoring Services")
    parser.add_argument("--api-only", action="store_true", help="Start only FastAPI")
    parser.add_argument("--dashboard-only", action="store_true", help="Start only Dashboard")
    parser.add_argument("--api-port", type=int, default=8000, help="FastAPI port")
    parser.add_argument("--dashboard-port", type=int, default=8501, help="Dashboard port")
    parser.add_argument("--skip-checks", action="store_true", help="Skip dependency checks")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check dependencies
    if not args.skip_checks:
        if not check_dependencies():
            print("\n❌ Please install dependencies first: pip install -r requirements.txt")
            sys.exit(1)
        
        check_model()
    
    processes = []
    
    try:
        # Start services
        if not args.dashboard_only:
            api_process = start_fastapi(args.api_port)
            if api_process:
                processes.append(("FastAPI", api_process))
        
        if not args.api_only:
            dashboard_process = start_dashboard(args.dashboard_port)
            if dashboard_process:
                processes.append(("Dashboard", dashboard_process))
        
        if processes:
            print("\n" + "="*60)
            print("✅ Services started successfully!")
            print("="*60)
            print("\nPress Ctrl+C to stop all services\n")
            
            # Wait for processes
            try:
                for name, process in processes:
                    process.wait()
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping services...")
                for name, process in processes:
                    process.terminate()
                    print(f"  ✓ {name} stopped")
        else:
            print("\n❌ No services started")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        for name, process in processes:
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()

