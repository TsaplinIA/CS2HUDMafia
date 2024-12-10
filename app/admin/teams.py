from starlette_admin.contrib.sqla import ModelView

from app.database import Team

teams_model_view = ModelView(Team)
