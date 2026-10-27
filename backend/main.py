"""
InsureVisionAI Backend Application Entrypoint.
Initializes FastAPI, configures CORS, registers API routers under /api/v1,
initializes CSV persistence, and sets up global error handling.
"""

import os
from contextlib import asynccontextmanager
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

from routes.analysis import router as analysis_router
from routes.auth import router as auth_router
from routes.contacts import router as contacts_router
from routes.dashboard import router as dashboard_router
from routes.incidents import router as incidents_router
from routes.insurance import router as insurance_router
from routes.reports import router as reports_router
from routes.services import router as services_router
from routes.chat import router as chat_router
from routes.sos import assistance_router, sos_router
from services.csv_storage import csv_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler.
    Initializes CSV storage and seeds demo records idempotently on startup.
    """
    csv_storage.initialize_storage()
    yield


app = FastAPI(
    title="InsureVisionAI API",
    description=(
        "Intelligent Road-Safety, Accident-Analysis, Insurance-Support, "
        "and Emergency-Assistance Backend Engine."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ==========================================
# CORS Configuration
# ==========================================

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins:
    configured_origins = [orig.strip() for orig in env_origins.split(",") if orig.strip()]
else:
    configured_origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Global Exception Handlers
# ==========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Ensure uniform error payloads for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        },
        headers=getattr(exc, "headers", None)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Ensure clean, understandable error payloads for schema validation errors."""
    errors = exc.errors()
    first_msg = errors[0].get("msg", "Validation error") if errors else "Invalid request data."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": f"Validation Error: {first_msg}",
            "status_code": 422,
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler preventing raw internal stack trace exposure."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected internal server error occurred.",
            "status_code": 500
        }
    )


# ==========================================
# Health Check Endpoint
# ==========================================

@app.get("/health", tags=["System"])
def health_check():
    """
    System Health Check Endpoint.
    Returns status, application identity, storage medium, and version.
    """
    return {
        "status": "ok",
        "application": "InsureVisionAI",
        "storage": "CSV",
        "version": "1.0.0"
    }


# ==========================================
# Register API Routers under /api/v1
# ==========================================

API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")

app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(dashboard_router, prefix=API_V1_PREFIX)
app.include_router(incidents_router, prefix=API_V1_PREFIX)
app.include_router(analysis_router, prefix=API_V1_PREFIX)
app.include_router(insurance_router, prefix=API_V1_PREFIX)
app.include_router(services_router, prefix=API_V1_PREFIX)
app.include_router(chat_router, prefix=API_V1_PREFIX)
app.include_router(sos_router, prefix=API_V1_PREFIX)
app.include_router(assistance_router, prefix=API_V1_PREFIX)
app.include_router(reports_router, prefix=API_V1_PREFIX)
app.include_router(contacts_router, prefix=API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)

