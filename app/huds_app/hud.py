import json
import os

from collections import deque
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
import urllib.parse
from timeit import timeit

import msgspec.json
from sqlalchemy import Sequence
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from app.config import get_huds_dir


@dataclass
class HUD:
    name: str
    hud_dir: str
    static_dirs: dict[str, str | Sequence] = field(default_factory=dict)
    _templates = None

    @property
    def _static_dirs(self):
        return {"css": "", "js": "", "templates": "", "root": ""} | self.static_dirs

    def _path_value_to_path(self, path: str | Sequence[str]) -> str:
        if isinstance(path, (str, bytes, PathLike)):
            path_seq = (path,)
        elif isinstance(path, Sequence):
            path_seq = path
        else:
            raise TypeError("path must be PathLike str or Sequence[PathLike]")
        flat_path_seq = deque([self.hud_dir])
        for path_el in path_seq:
            try:
                flat_path_seq.append(Path(path_el))
            except TypeError:
                raise TypeError("path must be PathLike or Sequence[PathLike]")
        return os.fspath(Path(os.path.join(*flat_path_seq)))

    def get_static_web_path(self, static_name: str) -> str:
        static_fs_path = self.get_static_file_path(static_name)
        return urllib.parse.urljoin("/", static_fs_path.replace("\\", "/"))

    def get_static_file_path(self, static_name: str) -> str:
        static_path = self._static_dirs.get(static_name)
        if static_path is None:
            raise ValueError("static path not found")
        return self._path_value_to_path(static_path)

    @property
    def template_fs_abspath(self):
        path = self._static_dirs["templates"]
        return os.fspath(Path(os.path.join(get_huds_dir(), self._path_value_to_path(path))))

    @property
    def templates(self):
        if self._templates is None:
            self._templates = Jinja2Templates(
                self.template_fs_abspath, extensions=["jinja2.ext.i18n", "pypugjs.ext.jinja.PyPugJSExtension"]
            )
        return self._templates

    _encoder = msgspec.json.Encoder()
    _encoding_types = (bool,)

    def get_initial_context(self, request: Request):
        data = {
            "delay": 0,
            "anim": request.url_for("huds", path=f"{self.get_static_web_path('root')}/animate.css"),
            "css": request.url_for("huds", path=f"{self.get_static_web_path('css')}/style.css"),
            "ip": "localhost",
            "port": 8080,
            "print_player_data": False,
            "hud": request.url_for("huds", path=f"{self.get_static_web_path('root')}/index.js"),
            "display_avatars": False,
            "display_player_avatars": False,
            "display_team_flags": False,
            "display_player_flags": False,
            "displayOnlyMainImage": False,
            "displayScoreboard": False,
            "displayRadar": False,
        }
        for k, v in data.items():
            if isinstance(v, self._encoding_types):
                data[k] = self._encoder.encode(v).decode()

        data = data | {"request": request}

        return data
