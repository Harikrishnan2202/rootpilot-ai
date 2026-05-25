from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

from .config import Config
from .routes import analyze_router, logs_router, chat_router
from .models import HealthResponse

# Create FastAPI app
app = FastAPI(
    title="RootPilot AI - Incident Root Cause Analyzer",
    description="AI-powered incident analysis for SRE teams",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze_router)
app.include_router(logs_router)
app.include_router(chat_router)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic info."""
    return {
        "name": "RootPilot AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Root"])
async def health_check():
    """Comprehensive health check endpoint."""
    return HealthResponse(
        status="healthy",
        llm_provider=Config.LLM_PROVIDER,
        timestamp=datetime.now().isoformat()
    )

# Optional: startup event to validate config
@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup."""
    try:
        Config.validate()
        print("[OK] RootPilot AI backend started successfully")
        print(f"[INFO] LLM Provider: {Config.LLM_PROVIDER}")
        print(f"[INFO] CORS Origins: {Config.CORS_ORIGINS}")
        print(f"[INFO] Server will run on http://{Config.HOST}:{Config.PORT}")
    except ValueError as e:
        print(f"[WARN] Configuration error: {e}")
        print("Please check your .env file and ensure API keys are set correctly.")
        # Don't raise, allow app to start but endpoints will fail gracefully

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True
    )
