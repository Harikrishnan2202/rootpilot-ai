#!/usr/bin/env python3
"""
RootPilot AI Backend Launcher
Run this script to start the FastAPI server.
"""

import uvicorn
from app.config import Config

if __name__ == "__main__":
    print("[*] Starting RootPilot AI Backend...")
    print(f"[+] LLM Provider: {Config.LLM_PROVIDER}")
    print(f"[+] Server: http://{Config.HOST}:{Config.PORT}")
    print(f"[+] API Docs: http://{Config.HOST}:{Config.PORT}/docs")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True,
        log_level="info"
    )