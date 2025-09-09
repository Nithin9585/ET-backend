#!/usr/bin/env python3
"""
Production startup script for OCR PII Detection API
"""
import uvicorn
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from config.logging import logger

def main():
    """Start the production server."""
    logger.info("Starting OCR PII Detection API server...")
    logger.info(f"Configuration loaded: Debug={settings.debug}, Host={settings.host}, Port={settings.port}")
    
    # Start the server
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers if not settings.debug else 1,
        log_level=settings.log_level.lower(),
        access_log=True,
        reload=settings.debug,
        timeout_keep_alive=settings.request_timeout,
    )

if __name__ == "__main__":
    main()
