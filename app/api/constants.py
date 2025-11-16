from fastapi import HTTPException, APIRouter
from pydantic import BaseModel, ValidationError
from typing import Any

from app.config import constants, Constants


class ResponseModel(BaseModel):
    message: str


constants_router = APIRouter(prefix="/constants", tags=["constants"])


@constants_router.post("/", response_model=ResponseModel, status_code=200)
async def validate_fields(input_data: dict[str, Any]):
    valid_data = {}
    for key, value in input_data.items():
        if not hasattr(constants, key):
            raise HTTPException(status_code=422, detail=f"Constant '{key}' does not exist.")
        try:
            constants.model_validate({key: value}, strict=True)
        except ValidationError:
            raise HTTPException(status_code=422, detail=f"Constant '{key}' can't be {value}.")
        valid_data[key] = value
    for key, value in valid_data.items():
        setattr(constants, key, value)
    return {"message": "OK"}

@constants_router.get("/", response_model=Constants, status_code=200)
async def get_constants():
    return constants