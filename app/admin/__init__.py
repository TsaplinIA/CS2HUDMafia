from starlette.requests import Request
from starlette_admin.contrib.sqla import Admin as SQLAAdmin

from app.admin.players import players_model_view
from app.admin.teams import teams_model_view
from app.database import engine
from app.config import settings, get_template_dir


class Admin(SQLAAdmin):
    def custom_render_js(self, request: Request):
        return request.url_for("js", path="custom_render.js")


def init_admin(engine, title="Example: SQLAlchemy", base_url="/"):
    admin = Admin(
        engine,
        title=title,
        base_url=base_url,
        templates_dir=get_template_dir(),
    )

    admin.add_view(teams_model_view)
    admin.add_view(players_model_view)

    admin.add_view(match_page_view)
    return admin


admin = init_admin(engine, title=settings.app_name)
