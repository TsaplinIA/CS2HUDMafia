from dataclasses import dataclass
from typing import Any

from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.contrib.sqla.fields import _serialize_sqlalchemy_file_library

from app.utils.steam_utils import get_player_info_async
from app.database.players import Player
from starlette_admin import StringField, RequestAction, BaseField, ImageField

from app.models.players import SteamPlayerSchema
from app.database import Team
from app.config import get_template_dir

local_templates = Jinja2Templates(get_template_dir(), autoescape=True)
nickname_template = local_templates.get_template("nicknames.html")
steam_id_template = local_templates.get_template("steam_id.html")
team_template = local_templates.get_template("team.html")

steam_question_avatar_url = "https://avatars.fastly.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_medium.jpg"


@dataclass
class NicknamesField(StringField):
    render_function_key: str = "template"

    async def serialize_value(self, request: Request, value: Any, action: RequestAction) -> Any:
        if action == RequestAction.LIST:
            return nickname_template.render({"names": value, "max_name_length": 12})
        return await super().serialize_value(request, value, action)

    async def parse_obj(self, request: Request, obj: Any) -> Any:
        assert isinstance(obj, Player)
        return (obj.displayed_name, obj.steam_name, obj.real_name)


@dataclass
class SteamId64Field(StringField):
    render_function_key: str = "template"

    async def serialize_value(self, request: Request, value: Any, action: RequestAction) -> Any:
        if action == RequestAction.LIST:
            return steam_id_template.render(value)
        return await super().serialize_value(request, value, action)

    async def parse_obj(self, request: Request, obj: Any) -> Any:
        assert isinstance(obj, Player)
        return {"steam_id": obj.steam_id, "steam_profile_url": obj.steam_profile_url}


@dataclass
class MergedAvatarsField(BaseField):
    render_function_key: str = "image"

    async def serialize_value(self, request: Request, value: Any, action: RequestAction) -> Any:
        data = []
        default_image = {"url": steam_question_avatar_url}
        if action == RequestAction.LIST:
            data.append(
                _serialize_sqlalchemy_file_library(request, value["avatar"], action, False)
                if value["avatar"]
                else default_image
            )
            data.append({"url": value["steam_avatar_medium"]} if value["steam_avatar_medium"] else default_image)
            return data
        return await super().serialize_value(request, value, action)

    async def parse_obj(self, request: Request, obj: Any) -> Any:
        assert isinstance(obj, Player)
        return {"avatar": obj.avatar, "steam_avatar_medium": obj.steam_avatar_medium}


@dataclass
class TeamField(ImageField):
    render_function_key: str = "template"

    async def serialize_value(self, request: Request, value: Any, action: RequestAction) -> Any:
        if action == RequestAction.LIST:
            if value is None:
                return None
            assert isinstance(value, Team)
            if value.logo:
                image_url = _serialize_sqlalchemy_file_library(request, value.logo, action, False)["url"]
            else:
                image_url = steam_question_avatar_url

            return team_template.render({"team_logo": image_url, "team_name": value.name})
        return await super().serialize_value(request, value, action)

    async def parse_obj(self, request: Request, obj: Any) -> Any:
        assert isinstance(obj, Player)
        return obj.team


class PlayerView(ModelView):
    fields = [
        "id",
        "steam_id",
        "avatar",
        TeamField("team_field", label="Team"),
        MergedAvatarsField("avatars", label="Avatars"),
        NicknamesField("names", label="Names"),
        SteamId64Field("steam_id_copy", label="SteamID64"),
        "real_name",
        "displayed_name",
        "team",
    ]
    fields_default_sort = ["team"]
    exclude_fields_from_list = [
        Player.id,
        Player.steam_id,
        Player.real_name,
        Player.displayed_name,
        Player.avatar,
        "team",
    ]
    exclude_fields_from_create = [Player.id, "names", "steam_id_copy", "avatars", "team_field"]
    exclude_fields_from_edit = [Player.id, "names", "steam_id_copy", "avatars", "team_field"]

    sortable_fields = ["steam_id", "team"]
    searchable_fields = ["real_name", "displayed_name", "team", "steam_id", "id"]

    async def before_create(self, request: Request, data: dict[str, Any], obj: Any) -> None:
        steam_id = data["steam_id"]
        steam_data: SteamPlayerSchema = await get_player_info_async(steam_id)
        assert isinstance(obj, Player)
        obj.steam_name = steam_data.steam_name
        obj.steam_profile_url = str(steam_data.steam_profile_url)
        obj.steam_avatar_small = str(steam_data.steam_avatar_small)
        obj.steam_avatar_medium = str(steam_data.steam_avatar_medium)
        obj.steam_avatar_full = str(steam_data.steam_avatar_full)


players_model_view = PlayerView(Player, label="Players")
