from typing import Union

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_file import File, ImageField
from sqlalchemy_file.validators import SizeValidator

from app.database.base import Base
from app.database.teams import Team


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    steam_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    real_name: Mapped[str] = mapped_column(nullable=True, index=True)
    displayed_name: Mapped[str] = mapped_column(nullable=True, index=True)
    avatar: Union[File, None] = Column(
        ImageField(
            upload_storage="user-avatar",
            thumbnail_size=(128, 128),
            validators=[SizeValidator(max_size="5M")],
        )
    )
    steam_name: Mapped[str] = mapped_column(String(256), nullable=True, index=True)
    steam_profile_url: Mapped[str] = mapped_column(String(512), nullable=True)
    steam_avatar_small: Mapped[str] = mapped_column(String(512), nullable=True)
    steam_avatar_medium: Mapped[str] = mapped_column(String(512), nullable=True)
    steam_avatar_full: Mapped[str] = mapped_column(String(512), nullable=True)
    team_id = mapped_column(ForeignKey("teams.id"))
    team = relationship(Team)
