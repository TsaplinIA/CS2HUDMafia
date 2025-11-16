import os
import sys
from json import JSONDecodeError
from typing import Optional, Literal

from pydantic import ValidationError
from pydantic_settings import BaseSettings
import logging

constants_logger = logging.getLogger("constants")


class Settings(BaseSettings):
    app_name: str = "CS2HUDMafia"
    server_host: str = "localhost"
    server_port: int = 8001
    steam_apikey: str = "STEAM_APIKEY"
    POSTGRES_URL: str | None = None
    storage_path: str = "storage"

    MINIO_HOST: str | None = None  # или "minio.my-domain.com"
    MINIO_PORT: int | None = None  # если прокинешь через nginx на 443 — поставь 443 и secure=True
    MINIO_ACCESS_KEY: str | None = None
    MINIO_SECRET_KEY: str | None = None
    MINIO_SECURE:bool = False  # True, если HTTPS

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        env_file_encoding = "utf-8"

    _upload_dir = None

    @property
    def upload_dir(self):
        if self._upload_dir is None:
            self._upload_dir = os.path.join(get_storage_dir(), "upload")
        return self._upload_dir

    @property
    def database_url(self):
        if self.POSTGRES_URL:
            return self.POSTGRES_URL
        return f"sqlite:///{os.path.join(get_storage_dir(), 'test.db')}"

settings = Settings()

def get_base_dir() -> str:
    """
    Папка приложения:
    - при обычном запуске: корень проекта
    - при запуске из exe: папка, где лежит server.exe
    """
    if getattr(sys, "frozen", False):
        # PyInstaller
        return os.path.dirname(sys.executable)
    # обычный запуск — идём от этого файла вверх
    return os.path.dirname(os.path.abspath(__file__))


def get_resources_dir() -> str:
    """
    Папка, где лежат вшитые ресурсы:
    - при обычном запуске: корень проекта (как раньше)
    - при запуске из exe: временная папка PyInstaller (sys._MEIPASS)
    """
    if getattr(sys, "frozen", False):
        # PyInstaller распаковывает туда --add-data
        return sys._MEIPASS  # type: ignore[attr-defined]
    return get_base_dir()


def get_assets_dir() -> str:
    return os.path.join(get_resources_dir(), "assets")


def get_huds_dir() -> str:
    return os.path.join(get_resources_dir(), "huds")


def get_template_dir() -> str:
    return os.path.join(get_assets_dir(), "templates")


def get_storage_dir() -> str:
    if os.path.isabs(settings.storage_path):
        return settings.storage_path
    return os.path.join(get_base_dir(), settings.storage_path)


constants_json_file_path: str = os.path.join(get_storage_dir(), "constants.json")


class Constants(BaseSettings):
    display_avatars: bool = True

    team_left_id: Optional[int] = None
    team_right_id: Optional[int] = None
    team_auto_detect: bool = False

    team_side_auto_detect: bool = False
    team_left_side: Literal["attack", "defence"] = "attack"

    match_type: Literal["bo1", "bo3", "bo5"] = "bo5"
    left_team_map_count: int = 0
    right_team_map_count: int = 0

    fake_loop_enabled: bool = True

    @property
    def team_right_side(self):
        sides = {"attack", "defence"}
        sides.remove(self.team_left_side)
        assert len(sides) == 1
        return sides.pop()

    def __setattr__(self, key, value):
        if key == "team_right_side":
            sides = {"attack", "defence"}
            assert value in sides
            sides.remove(value)
            key, value = "team_left_side", sides.pop()
        super().__setattr__(key, value)

    def save(self):
        with open(constants_json_file_path, "w") as file:
            file.write(self.model_dump_json(indent=4, exclude={"_json_file_path"}))

    @classmethod
    def load(cls):
        if not os.path.exists(constants_json_file_path):
            return Constants()
        with open(constants_json_file_path, "r") as file:
            try:
                obj = cls.model_validate_json(file.read())
            except (JSONDecodeError, ValidationError) as e:
                constants_logger.error(e)
                return Constants()
            else:
                return obj


constants = Constants.load()
