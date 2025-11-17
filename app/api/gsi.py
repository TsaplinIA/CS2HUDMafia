import json
from collections import defaultdict, Counter

import msgspec.msgpack
from cachetools import TTLCache, cached, LRUCache
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

from starlette.requests import Request

from app.config import constants
from app.database import get_session, Player as DBPlayer
from app.utils.gsi import HUDGSI, compare_struct, Player as GSIPlayer


class ResponseModel(BaseModel):
    message: str


gsi_router = APIRouter(prefix="/gsi", tags=["gsi"])

hud_gsi_decoder = msgspec.json.Decoder(HUDGSI)
unexpected_fields_global = set()

@gsi_router.post("/hud", response_model=ResponseModel, status_code=200)
async def listen_gsi(request: Request, input_data: dict[str, Any]):
    await request.app.sio.emit("update", input_data)
    js = await request.body()
    try:
        gsi_obj: HUDGSI = hud_gsi_decoder.decode(js)
    except (msgspec.ValidationError, Exception) as e:
        return {"message": str(e)}
    if gsi_obj.allplayers and isinstance(gsi_obj.allplayers, dict):
        await sync_player_list(request, gsi_obj.allplayers)

    if constants.team_auto_detect:
        teams = defaultdict(set)
        for steam_id, player in gsi_obj.allplayers.items():
            player: GSIPlayer
            team = player.team.lower()
            teams[team].add(steam_id)
        teams = {team: tuple(players) for team, players in teams.items()}
        t, ct = guess_teams(**teams)
        constants.team_left_id = t
        constants.team_right_id = ct
    return {"message": "OK"}


async def sync_player_list(request: Request, players: dict[str, GSIPlayer]):
    players_set = set(players.keys())
    for player in request.app.player_list:
        if player not in players_set:
            request.app.player_list.remove(player)
        else:
            players_set.remove(player)
    if not players_set:
        return
    with get_session() as session:
        existed_players = session.query(DBPlayer.steam_id).filter(DBPlayer.steam_id.in_(players_set)).all()
        existed_players = {pid for (pid,) in existed_players}

        for steam_id in players_set:
            request.app.player_list.add(steam_id)
            if steam_id in existed_players:
                continue
            gsi_player = players[steam_id]
            db_player = DBPlayer(
                steam_id=steam_id,
                steam_name=gsi_player.name,
            )
            session.add(db_player)
        session.commit()


_guess_cache= TTLCache(maxsize=10, ttl=60)

@cached(_guess_cache)
def guess_teams(t: tuple[str, ...], ct: tuple[str, ...]):
    """
    Возвращает по одной самой частой команде для T и CT.
    Формат как у Counter.most_common(1): список из одного (team_id, count) или пустой список.
    """
    id2team = get_id2team()

    def top_team(steam_ids: tuple[str, ...]):
        counter = Counter(
            team_id
            for steam_id in steam_ids
            if (team_id := id2team.get(steam_id)) is not None
        )
        return counter.most_common(1)


    res = top_team(t)
    top_t_team = res[0][0] if res else None
    res = top_team(ct)
    top_ct_team = res[0][0] if res else None

    return top_t_team, top_ct_team


_ids_cache = TTLCache(maxsize=1, ttl=60)

@cached(_ids_cache)
def get_id2team():
    with get_session() as session:
        players = session.query(DBPlayer.steam_id, DBPlayer.team_id).all()
        id2team = {steam_id: team_id for steam_id, team_id in players}
        return id2team