import json

import msgspec.msgpack
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

from starlette.requests import Request

from app.utils.gsi import HUDGSI, compare_struct


class ResponseModel(BaseModel):
    message: str


gsi_router = APIRouter(prefix="/gsi", tags=["gsi"])

hud_gsi_decoder = msgspec.json.Decoder(HUDGSI)
unexpected_fields_global = set()

@gsi_router.post("/hud", response_model=ResponseModel, status_code=200)
async def listen_gsi(request: Request, input_data: dict[str, Any]):
    await request.app.sio.emit("update", input_data)
    js = await request.body()

    gsi_dict = json.loads(js)
    unexpected_fields = compare_struct(HUDGSI, gsi_dict)
    for unexpected_field in unexpected_fields:
        if unexpected_field in unexpected_fields_global:
            continue
        unexpected_fields_global.add(unexpected_field)
        unexpected_field_str = '.'.join(unexpected_field)
        print(f"Unexpected field: {unexpected_field_str}")
        content = gsi_dict
        for key in unexpected_field:
            content = content.get(key)
        print(f"Example: {unexpected_field_str}: {content}")
        if 'added' in unexpected_field:
            print(gsi_dict['added'])
    try:
        gsi_obj: HUDGSI = hud_gsi_decoder.decode(js)
    except (msgspec.ValidationError, Exception) as e:
        return {"message": str(e)}
    if gsi_obj.allplayers and isinstance(gsi_obj.allplayers, dict):
        await sync_player_list(request, gsi_obj.allplayers)

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
        existed_players = session.query(DBPlayer.id).filter(DBPlayer.id.in_(players_set)).all()
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