import asyncio
import logging
from collections import deque
from collections.abc import Iterable
from itertools import islice
from time import sleep

import aiohttp
import requests

from app.database import get_session, Player
from app.models.players import SteamPlayerListSchema, SteamPlayerSchema
from app.config import settings

steam_logger = logging.getLogger("steamapi")

GET_PLAYER_SUMMARIES_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"


def chunk_iterable(iterable, chunk_size=10):
    it = iter(iterable)
    while chunk := list(islice(it, chunk_size)):
        yield chunk


async def update_all_players_info_async():
    with get_session() as session:
        players = session.query(Player).all()
        players_steam_ids = [player.steam_id for player in players]
        steam_data: dict[str, SteamPlayerSchema] = await get_players_info_async(players_steam_ids)
        for player in players:
            data: SteamPlayerSchema = steam_data.get(player.steam_id)
            if data is None:
                continue
            player.steam_name = data.steam_name
            player.steam_profile_url = data.steam_profile_url
            player.steam_avatar_small = data.steam_avatar_small
            player.steam_avatar_medium = data.steam_avatar_medium
            player.steam_avatar_full = data.steam_avatar_full


def get_players_info(player_list: Iterable) -> dict[str, SteamPlayerSchema]:
    player_list = deque(player_list)
    result = {}
    for players in chunk_iterable(player_list, 50):
        req = requests.models.PreparedRequest()
        req.prepare_url(GET_PLAYER_SUMMARIES_URL, params={"key": settings.steam_apikey, "steamids": ",".join(players)})
        while (resp := requests.get(req.url)).status_code != 200:
            steam_logger.warning(f"GET_PLAYER_SUMMARIES status is {resp.status_code}, text: {resp.text}")
            sleep(1)
        resp = requests.get(req.url)
        for steam_player in SteamPlayerListSchema.validate_python(resp.json()["response"]["players"]):
            result[steam_player.steam_id] = steam_player
    return result


def get_player_info(steam_id: str) -> SteamPlayerSchema:
    return get_players_info((steam_id,)).get(steam_id)


async def get_players_info_async(player_list: Iterable) -> dict[str, SteamPlayerSchema]:
    player_list = deque(player_list)
    result = {}
    semaphore = asyncio.Semaphore(10)

    async def fetch_players(players_chunk):
        async with semaphore:
            params = {
                "key": settings.steam_apikey,
                "steamids": ",".join(players_chunk),
            }
            async with aiohttp.ClientSession() as session:
                while True:
                    async with session.get(GET_PLAYER_SUMMARIES_URL, params=params) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data["response"]["players"]
                        else:
                            steam_logger.warning(
                                f"GET_PLAYER_SUMMARIES status is {resp.status}, text: {await resp.text()}"
                            )
                            await asyncio.sleep(1)

    tasks = [asyncio.create_task(fetch_players(players)) for players in chunk_iterable(player_list, 50)]

    for task in asyncio.as_completed(tasks):
        try:
            players_data = await task
            for steam_player in SteamPlayerListSchema.validate_python(players_data):
                result[steam_player.steam_id] = steam_player
        except Exception as e:
            steam_logger.error(f"Error fetching players: {e}")

    return result


async def get_player_info_async(steam_id: str) -> SteamPlayerSchema:
    return (await get_players_info_async((steam_id,))).get(steam_id)


if __name__ == "__main__":
    sids = ["76561198842315885", "76561198014624910", "76561198201668683", "76561198126842274", "76561198347779436"]
    ret = get_players_info(sids)
    print(ret)
