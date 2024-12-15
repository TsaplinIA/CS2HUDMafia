from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.admin import admin
from app.api.constants import constants_router
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles

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
    app.mount("/js", StaticFiles(directory="assets/js"), name="js")
    app.mount("/css", StaticFiles(directory="assets/css"), name="css")
    app.mount("/icons", StaticFiles(directory="assets/icons"), name="icons")
    init_logging_config()
    app.include_router(constants_router)
    admin.mount_to(app)
    return app


fastapi_app = init_app()
