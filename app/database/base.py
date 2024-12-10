import os
from contextlib import contextmanager

from libcloud.storage.providers import get_driver
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from libcloud.storage.types import Provider
from sqlalchemy_file.storage import StorageManager
from config import settings, get_storage_dir

os.makedirs(f"{settings.upload_dir}/avatars", 0o777, exist_ok=True)
player_container = get_driver(Provider.LOCAL)(settings.upload_dir).get_container("avatars")
StorageManager.add_storage("user-avatar", player_container)

os.makedirs(f"{settings.upload_dir}/logos", 0o777, exist_ok=True)
team_container = get_driver(Provider.LOCAL)(settings.upload_dir).get_container("logos")
StorageManager.add_storage("team-logo", team_container)


Base = declarative_base()
engine = create_engine(
    f"sqlite:///{os.path.join(get_storage_dir(), settings.database_name)}",
    connect_args={"check_same_thread": False},
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
