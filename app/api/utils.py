from fastapi import APIRouter
from starlette.requests import Request

utils_router = APIRouter(prefix="/utils")



@utils_router.post("/refresh")
async def refresh(request: Request):
    await request.app.sio.emit("refresh")
    return {"message": "OK"}