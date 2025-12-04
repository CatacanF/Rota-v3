from fastapi import APIRouter
from app.core.config import settings
import psutil
import time

router = APIRouter()

start_time = time.time()

@router.get("/")
async def get_stats():
    """
    Get API health and usage statistics.
    """
    current_time = time.time()
    uptime = current_time - start_time
    
    return {
        "status": "healthy",
        "uptime_seconds": uptime,
        "version": "1.0.0",
        "project": settings.PROJECT_NAME,
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent
        }
    }
