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
    # await request.app.sio.emit("update", input_data)
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
        gsi_obj = hud_gsi_decoder.decode(js)
    except msgspec.ValidationError as e:
        print(e, js)
    return {"message": "OK"}
