import os
from json import JSONDecodeError

from pydantic import ValidationError
from pydantic_settings import BaseSettings
import logging

constants_logger = logging.getLogger("constants")


class Settings(BaseSettings):
    app_name: str = "CS2HUDMafia"
    server_host: str = "localhost"
    server_port: int = 8001
    steam_apikey: str = "STEAM_APIKEY"
    database_name: str = "test.db"
    storage_path: str = "../storage"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"

    _upload_dir = None

    @property
    def upload_dir(self):
        if self._upload_dir is None:
            self._upload_dir = os.path.join(get_storage_dir(), "upload")
        return self._upload_dir


settings = Settings()


def get_template_dir() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "templates")


def get_storage_dir() -> str:
    if os.path.isabs(settings.storage_path):
        return settings.storage_path
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), settings.storage_path)


constants_json_file_path: str = os.path.join(get_storage_dir(), "constants.json")


class Constants(BaseSettings):
    display_avatars: bool = True

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