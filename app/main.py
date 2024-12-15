from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.admin import admin
from app.api.constants import constants_router
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles

from app.huds_app import hud_router
from app.logging import init_logging_config
from app.scheduler import init_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI start")
    scheduler = await init_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()
    print("FastAPI shutdown")


def init_app():
    Base.metadata.create_all(engine)
    app = FastAPI(lifespan=lifespan)
    init_logging_config()

    sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
    app.mount("/socket.io", socketio.ASGIApp(sio))
    app.sio = sio

    app.mount("/js", StaticFiles(directory=os.path.join(get_assets_dir(), "js")), name="js")
    app.mount("/css", StaticFiles(directory=os.path.join(get_assets_dir(), "css")), name="css")
    app.mount("/icons", StaticFiles(directory=os.path.join(get_assets_dir(), "icons")), name="icons")
    app.mount("/static/huds", StaticFiles(directory=get_huds_dir()), name="huds")
    app.mount("/files", StaticFiles(directory=os.path.join(get_assets_dir(), "files")), name="files")

    app.include_router(constants_router)
    app.include_router(hud_router)
    admin.mount_to(app)
    return app


fastapi_app = init_app()
