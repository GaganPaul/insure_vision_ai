# InsureVisionAI

An intelligent road-safety, accident-analysis, insurance-support, and emergency-assistance platform.

## Architecture

This repository hosts the **InsureVisionAI Backend**, built with FastAPI, Python 3.11+, and an atomic CSV persistent storage engine.

For complete backend architecture, installation, API specifications, and testing details, please refer to:
[backend/README.md](backend/README.md)

### Quick Start

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # On Windows
source .venv/bin/activate       # On Linux/macOS
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- **Swagger Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Demo Credentials**: `nuzair@email.com` / `123456` (Name: Nuzair)
