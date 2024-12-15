from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from app.huds_app.hud import HUD

huds = {
    "JT": HUD(
        name="JT",
        hud_dir="JohnTimmermann",
    )
}

hud_router = APIRouter(prefix="/huds", tags=["huds"], redirect_slashes=True)


@hud_router.get(path="/{name}")
def render_hud(request: Request, name: str):
    hud = huds.get(name)
    if hud is None:
        raise HTTPException(status_code=404)
    return hud.templates.TemplateResponse("template.pug", hud.get_initial_context(request=request))
