from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette_admin import CustomView

from app.config import constants


class MatchPage(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse(
            "match_page.html",
            {
                "request": request,
                "constants": constants,
            },
        )


class TestPage(CustomView):
    async def render(self, request: Request, templates: Jinja2Templates) -> Response:
        return templates.TemplateResponse("test.html", {"request": request})


match_page_view = MatchPage(label="Match", path="/match_page")
test_page_view = TestPage(label="Test")
