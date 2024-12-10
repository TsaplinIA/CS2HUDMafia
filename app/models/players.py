from pydantic import BaseModel, AliasChoices, Field, AnyHttpUrl, TypeAdapter


class SteamPlayerSchema(BaseModel):
    steam_id: str = Field(validation_alias=AliasChoices("steamid", "steam_id"))
    steam_name: str = Field(validation_alias=AliasChoices("personaname", "steam_name"))
    steam_profile_url: AnyHttpUrl = Field(validation_alias=AliasChoices("profileurl", "steam_profile_url"))
    steam_avatar_small: AnyHttpUrl = Field(validation_alias=AliasChoices("avatar", "steam_avatar_small"))
    steam_avatar_medium: AnyHttpUrl = Field(validation_alias=AliasChoices("avatarmedium", "steam_avatar_medium"))
    steam_avatar_full: AnyHttpUrl = Field(validation_alias=AliasChoices("avatarfull", "steam_avatar_full"))


SteamPlayerListSchema = TypeAdapter(list[SteamPlayerSchema])
