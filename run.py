import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
        access_log=False,  # disable access logs entirely
        log_level=settings.LOG_LEVEL.lower(),  # sync uvicorn level with settings
    )
