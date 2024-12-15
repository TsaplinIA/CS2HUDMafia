from pydantic import BaseModel, Field, AliasChoices


class TeamSchema(BaseModel):
    id: str = Field(validation_alias=AliasChoices("id", "_id"))
    team_name: str = Field(validation_alias=AliasChoices("name", "team_name"))
    short_name: str | None = Field(default=None, validation_alias=AliasChoices("short_name"))
    country_code: str | None = Field(default="default")
    logo_url: str | None = Field(default=None)
