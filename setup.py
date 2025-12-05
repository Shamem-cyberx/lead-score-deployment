"""
RAKEZ Lead Scoring - Setup Script
Automated setup and configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║     RAKEZ Lead Scoring Model - Setup Wizard                 ║
    ║     Setting up your environment...                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check Python version"""
    print("\n[1/6] Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} - Requires Python 3.9+")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n[2/6] Installing dependencies...")
    req_file = Path(__file__).parent / "requirements.txt"
    
    if not req_file.exists():
        print("  ✗ requirements.txt not found")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("  ✓ Dependencies installed successfully")
            return True
        else:
            print(f"  ⚠️  Some dependencies may have failed: {result.stderr[:200]}")
            return True  # Continue anyway
    except Exception as e:
        print(f"  ✗ Error installing dependencies: {e}")
        return False

def create_dummy_model():
    """Create dummy model for testing"""
    print("\n[3/6] Creating dummy MLflow model...")
    model_script = Path(__file__).parent / "03_api" / "create_dummy_model.py"
    
    if not model_script.exists():
        print("  ⚠️  Model creation script not found, skipping...")
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, str(model_script)],
            capture_output=True,
            text=True,
            cwd=model_script.parent
        )
        
        if result.returncode == 0 or "registered" in result.stdout.lower():
            print("  ✓ Dummy model created")
            return True
        else:
            print("  ⚠️  Model may already exist, continuing...")
            return True
    except Exception as e:
        print(f"  ⚠️  Could not create model: {e}")
        print("     You can create it manually later")
        return True

def create_env_file():
    """Create .env file template"""
    print("\n[4/6] Creating environment file template...")
    env_file = Path(__file__).parent / ".env.example"
    
    env_content = """# RAKEZ Lead Scoring - Environment Variables
# Copy this file to .env and fill in your values

# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-databricks-token

# MLflow Configuration
MLFLOW_TRACKING_URI=./mlruns
# For production: MLFLOW_TRACKING_URI=http://your-mlflow-server:5000

# Model Configuration
MODEL_STAGE=Production
SHADOW_MODEL_ENABLED=false

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Dashboard Configuration
DASHBOARD_PORT=8501
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("  ✓ Created .env.example file")
        return True
    except Exception as e:
        print(f"  ⚠️  Could not create .env file: {e}")
        return True

def verify_installation():
    """Verify installation"""
    print("\n[5/6] Verifying installation...")
    
    checks = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'streamlit': 'Streamlit',
        'mlflow': 'MLflow',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'plotly': 'Plotly'
    }
    
    all_ok = True
    for module, name in checks.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def print_next_steps():
    """Print next steps"""
    print("\n[6/6] Setup complete!")
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("\n1. Start the services:")
    print("   python start.py")
    print("\n2. Or start individually:")
    print("   # FastAPI:")
    print("   cd 03_api && uvicorn fastapi_app:app --port 8000")
    print("   # Dashboard:")
    print("   cd 05_dashboard && streamlit run streamlit_dashboard.py")
    print("\n3. Access services:")
    print("   - API Docs: http://localhost:8000/docs")
    print("   - Dashboard: http://localhost:8501")
    print("\n4. For production deployment:")
    print("   - Configure Databricks connection")
    print("   - Set up MLflow tracking server")
    print("   - Deploy notebooks to Databricks")
    print("\n" + "="*60)

def main():
    print_banner()
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Please upgrade to Python 3.9 or higher")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        print("   Try manually: pip install -r requirements.txt")
        sys.exit(1)
    
    # Create dummy model
    create_dummy_model()
    
    # Create env file
    create_env_file()
    
    # Verify installation
    if not verify_installation():
        print("\n⚠️  Some packages are missing. Please install them manually.")
        print("   Run: pip install -r requirements.txt")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()

