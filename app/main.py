import os
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.admin import admin
from app.api.constants import constants_router
from app.api.gsi import gsi_router
from app.api.players import players_router
from app.api.teams import teams_router
from app.api.utils import utils_router
from app.config import get_assets_dir, get_huds_dir
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles

from app.huds_app import hud_router
from app.logging_filters import init_logging_config
from app.scheduler import init_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI, *args, **kwargs):
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

    app.player_list = set()

    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

    app.mount("/js", StaticFiles(directory=os.path.join(get_assets_dir(), "js")), name="js")
    app.mount("/css", StaticFiles(directory=os.path.join(get_assets_dir(), "css")), name="css")
    app.mount("/icons", StaticFiles(directory=os.path.join(get_assets_dir(), "icons")), name="icons")
    app.mount("/static/huds", StaticFiles(directory=get_huds_dir()), name="huds")
    app.mount("/files", StaticFiles(directory=os.path.join(get_assets_dir(), "files")), name="files")

    app.include_router(constants_router)
    app.include_router(gsi_router)
    app.include_router(hud_router)
    app.include_router(utils_router)
    app.include_router(teams_router, prefix="/api")
    app.include_router(players_router, prefix="/api")

    admin.mount_to(app)
    return app


fastapi_app = init_app()
