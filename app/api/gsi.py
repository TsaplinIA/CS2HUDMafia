from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

from starlette.requests import Request


class ResponseModel(BaseModel):
    message: str


gsi_router = APIRouter(prefix="/gsi", tags=["gsi"])


@gsi_router.post("/hud", response_model=ResponseModel, status_code=200)
async def listen_gsi(request: Request, input_data: dict[str, Any]):
    await request.app.sio.emit("update", input_data)
    return {"message": "OK"}
