# 📝 Environment Variables Guide

## Quick Start

1. **Copy the example file:**
   ```bash
   # Windows
   copy env.example .env
   
   # Linux/Mac
   cp env.example .env
   ```

2. **Edit `.env` with your values:**
   ```bash
   # Use your preferred editor
   notepad .env        # Windows
   nano .env           # Linux/Mac
   code .env           # VS Code
   ```

3. **Never commit `.env` to Git!**
   - `.env` should be in `.gitignore`
   - Only commit `env.example`

## Required Variables

### Minimum Setup (Local Development)

For basic local development, you only need:
```bash
MLFLOW_TRACKING_URI=./mlruns
MODEL_STAGE=Production
```

All other variables have defaults and are optional.

## Currently Used Variables

Based on the codebase, these environment variables are **actually used**:

### ✅ Used in Code

1. **`MODEL_STAGE`** (fastapi_app.py)
   - Default: `"Production"`
   - Purpose: Which MLflow model stage to load

2. **`SHADOW_MODEL_ENABLED`** (fastapi_app.py)
   - Default: `"false"`
   - Purpose: Enable/disable shadow deployment

3. **`MLFLOW_TRACKING_URI`** (create_dummy_model.py)
   - Default: `"./mlruns"`
   - Purpose: MLflow tracking server location

4. **`AUDIT_TABLE`** (audit_logging.py)
   - Default: `"default.audit_logs"`
   - Purpose: Delta table for audit logs

5. **`AUDIT_RETENTION_DAYS`** (audit_logging.py)
   - Default: `2555` (7 years)
   - Purpose: How long to keep audit logs

6. **`APPROVAL_TABLE`** (model_approval.py)
   - Default: `"default.model_approvals"`
   - Purpose: Delta table for model approvals

### 📋 Recommended for Production

These are not currently used but recommended:

- `ALLOWED_ORIGINS` - CORS configuration
- `API_KEY` - API authentication
- `DATABRICKS_HOST` - Databricks workspace
- `DATABRICKS_TOKEN` - Databricks authentication
- `DB_HOST`, `DB_PORT`, `DB_NAME` - Database connection
- `OLLAMA_URL` - Ollama server location

## Variable Categories

### 🔧 Core Configuration
- `MLFLOW_TRACKING_URI` - Where MLflow stores models
- `MODEL_STAGE` - Which model stage to use (Production/Staging)
- `API_PORT` - FastAPI server port (default: 8000)
- `DASHBOARD_PORT` - Dashboard port (default: 8050)

### 🔐 Security (Production)
- `ALLOWED_ORIGINS` - CORS allowed origins
- `API_KEY` - API authentication key
- `JWT_SECRET` - JWT token secret
- `ENCRYPTION_KEY` - Data encryption key

### ☁️ Databricks (Optional)
- `DATABRICKS_HOST` - Databricks workspace URL
- `DATABRICKS_TOKEN` - Authentication token
- `DATABRICKS_CLUSTER_ID` - Cluster for jobs

### 🗄️ Database (Optional)
- `DB_HOST`, `DB_PORT`, `DB_NAME` - Database connection
- `DATABASE_URL` - Alternative connection string

### 📊 Monitoring (Optional)
- `SMTP_*` - Email alerts
- `SLACK_WEBHOOK_URL` - Slack notifications

## Environment-Specific Configs

### Development
```bash
ENVIRONMENT=development
DEBUG=true
ALLOWED_ORIGINS=*
MLFLOW_TRACKING_URI=./mlruns
```

### Production
```bash
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://app.rakez.com,https://dashboard.rakez.com
MLFLOW_TRACKING_URI=databricks://profile-name
# Set all security keys
```

## Loading Environment Variables

### Python (using python-dotenv)
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env file

model_stage = os.getenv("MODEL_STAGE", "Production")
```

**Note:** Install `python-dotenv` first:
```bash
pip install python-dotenv
```

### Bash/Shell
```bash
# Load .env file
source .env
# or
export $(cat .env | xargs)
```

## Security Best Practices

1. ✅ **Never commit `.env`** - Add to `.gitignore`
2. ✅ **Use `env.example`** - Template with no secrets
3. ✅ **Rotate keys regularly** - Especially in production
4. ✅ **Use secrets management** - AWS Secrets Manager, Azure Key Vault, etc.
5. ✅ **Limit access** - Only necessary people should see `.env`

## Adding .env to .gitignore

If `.gitignore` doesn't exist, create it:

```bash
# .gitignore
.env
*.env
!env.example
__pycache__/
*.pyc
mlruns/
*.log
```

## Troubleshooting

### Variables not loading?
- Check `.env` file exists in project root
- Verify variable names match exactly (case-sensitive)
- Check for typos or extra spaces
- Install `python-dotenv`: `pip install python-dotenv`

### Default values not working?
- Check variable is not set elsewhere
- Verify `.env` file is being loaded
- Check for conflicting environment variables

## See Also

- `env.example` - Complete example file
- `SETUP_GUIDE.md` - Setup instructions
- `README.md` - Project documentation
- `INDEX.md` - Navigation guide



