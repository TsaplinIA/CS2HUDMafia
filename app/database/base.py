import os
from contextlib import contextmanager

from libcloud.storage.providers import get_driver
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from libcloud.storage.types import Provider, ContainerAlreadyExistsError
from sqlalchemy_file.storage import StorageManager
from app.config import settings


def get_or_create_container(driver, name: str):
    try:
        driver.create_container(container_name=name)
    except ContainerAlreadyExistsError:
        pass
    return driver.get_container(container_name=name)

if not settings.MINIO_HOST:
    os.makedirs(f"{settings.upload_dir}/avatars", 0o777, exist_ok=True)
    os.makedirs(f"{settings.upload_dir}/logos", 0o777, exist_ok=True)
    player_container = get_driver(Provider.LOCAL)(settings.upload_dir).get_container("avatars")
    team_container = get_driver(Provider.LOCAL)(settings.upload_dir).get_container("logos")
else:
    Cls = get_driver(Provider.MINIO)
    driver = Cls(
        settings.MINIO_ACCESS_KEY,
        settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
        host=settings.MINIO_HOST,
        port=settings.MINIO_PORT,
    )
    player_container = get_or_create_container(driver, "avatars")
    team_container = get_or_create_container(driver, "logos")


StorageManager.add_storage("user-avatar", player_container)
StorageManager.add_storage("team-logo", team_container)


Base = declarative_base()
if 'sqlite' not in settings.database_url:
    kwargs = {"pool_pre_ping": True}
else:
    kwargs = {"connect_args": {"check_same_thread": False}}

engine = create_engine(
    settings.database_url,
    **kwargs,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = scoped_session(SessionLocal)


@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
