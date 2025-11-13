from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView


class VideoplayerPage(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            "videoplayer.html",
            {
                "request": request,
            },
        )


videoplayer_view = VideoplayerPage(label="Videoplayer", path="/videoplayer")
