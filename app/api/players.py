from fastapi import APIRouter
from sqlalchemy_file import File
from starlette.requests import Request

from app.database import get_session, Player
from app.models.players import PlayerSchema

players_router = APIRouter(prefix="/players", tags=["players"], redirect_slashes=True)


@players_router.get("", status_code=200)
async def get_players(request: Request):
    res = []
    with get_session() as session:
        players = session.query(Player).all()
        for player in players:
            if isinstance(player.avatar, File):
                logo_path = player.avatar.path
                storage, file_id = logo_path.split("/")
                avatar_url = str(
                    request.url_for(
                        "admin:api:file",
                        storage=storage,
                        file_id=file_id,
                    )
                )
            else:
                avatar_url = None

            p = PlayerSchema(
                id=player.id,
                steam_id=player.steam_id,
                real_name=player.real_name,
                displayed_name=player.displayed_name,
                team_id=player.team_id,
                avatar_url=avatar_url,
                steam_avatar_url=player.steam_avatar_medium,
            )
            res.append(p)
    return {"players": res}


@players_router.get("/{steam_id}", status_code=200)
def get_player(request: Request, steam_id: str):
    with get_session() as session:
        player = session.query(Player).filter(Player.steam_id == steam_id).first()
        if isinstance(player.avatar, File):
            logo_path = player.avatar.path
            storage, file_id = logo_path.split("/")
            avatar_url = str(
                request.url_for(
                    "admin:api:file",
                    storage=storage,
                    file_id=file_id,
                )
            )
        else:
            avatar_url = None
        return PlayerSchema(
            id=player.id,
            steam_id=player.steam_id,
            real_name=player.real_name,
            displayed_name=player.displayed_name,
            team_id=player.team_id,
            avatar_url=avatar_url,
            steam_avatar_url=player.steam_avatar_medium
        )
