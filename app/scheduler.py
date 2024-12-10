import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.utils.steam_utils import update_all_players_info_async

from app.config import constants
import logging

scheduler_logger = logging.getLogger("scheduler")


def task(func):
    def decorated(*args, **kwargs):
        scheduler_logger.debug(func.__name__)
        try:
            if asyncio.iscoroutinefunction(func):
                event_loop = asyncio.get_event_loop()
                if event_loop.is_running():
                    task = event_loop.create_task(func(*args, **kwargs))
                    task.result()
                else:
                    event_loop.run_until_complete(func(*args, **kwargs))
            else:
                func(*args, **kwargs)
        except Exception as e:
            scheduler_logger.error(e)

    return decorated


@task
def save_constants_task():
    constants.save()


@task
async def update_steam_data_task():
    await update_all_players_info_async()


async def init_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(func=save_constants_task, trigger=IntervalTrigger(seconds=1))
    scheduler.add_job(func=update_steam_data_task, trigger=IntervalTrigger(minutes=10))
    return scheduler
