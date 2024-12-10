import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run("app:fastapi_app", host=settings.server_host, port=settings.server_port)
