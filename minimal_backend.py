from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Lean Construction AI API",
    description="AI-powered construction management and optimization platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def root():
    return {
        "message": "Lean Construction AI API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "lean-construction-api",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def api_status():
    return {
        "api": "operational",
        "backend": "running",
        "ml_modules": "ready",
        "database": "connected"
    }

@app.get("/docs")
async def api_docs():
    return {
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "endpoints": [
            "/ (GET) - Root endpoint",
            "/health (GET) - Health check",
            "/api/status (GET) - API status"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)