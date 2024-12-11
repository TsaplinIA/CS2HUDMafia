from typing import Union

from jinja2 import Template
from sqlalchemy import Column
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_file import File, ImageField
from sqlalchemy_file.validators import SizeValidator
from starlette.requests import Request

from app.database.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    short_name: Mapped[str]
    logo: Union[File, None] = Column(
        ImageField(
            upload_storage="user-avatar",
            thumbnail_size=(128, 128),
            validators=[SizeValidator(max_size="5M")],
        )
    )

    async def __admin_select2_repr__(self, request: Request) -> str:
        url = None
        if self.logo is not None:
            storage, file_id = self.logo.path.split("/")
            url = request.url_for(
                request.app.state.ROUTE_NAME + ":api:file",
                storage=storage,
                file_id=file_id,
            )
        default_url = "https://avatars.fastly.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_medium.jpg"
        template_str = """
        <div class="d-flex align-items-center">
            <span class="me-2 avatar avatar-xs" 
                style="background-image: url({{url}}); --tblr-avatar-size: 3rem;">
                {% if not url %}{{ obj.full_name[:2] }}{% endif %}
            </span>
            {{ obj.name }} ({{ obj.short_name }})
        </div>
        """

        return Template(template_str, autoescape=True).render(obj=self, url=(url or default_url))
