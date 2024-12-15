from fastapi import APIRouter
from sqlalchemy_file import File
from starlette.requests import Request

from app.database import get_session, Team
from app.models.teams import TeamSchema

teams_router = APIRouter(prefix="/teams", tags=["teams"], redirect_slashes=True)


@teams_router.get("", status_code=200)
async def get_teams(request: Request):
    res = []
    with get_session() as session:
        teams = session.query(Team).all()
        for team in teams:
            if isinstance(team.logo, File):
                logo_path = team.logo.path
                # if getattr(team.logo, "thumbnail", None) is not None:
                #     logo_path = team.logo.thumbnail.path
                storage, file_id = logo_path.split("/")
                logo_url = str(
                    request.url_for(
                        "admin:api:file",
                        storage=storage,
                        file_id=file_id,
                    )
                )
            else:
                logo_url = None

            t = TeamSchema(
                team_name=team.name,
                short_name=team.short_name,
                country_code="default",
                id=str(team.id),
                logo_url=logo_url,
            )
            res.append(t)
    return {"teams": res}
