import asyncio
import json
import os.path
import threading
from collections import deque
from dataclasses import dataclass


import httpx


from app.config import get_assets_dir, constants, settings


@dataclass
class FakeLoop:
    fake_loop_json = os.path.join(get_assets_dir(), "gsi_dump.json")
    fake_loop_list = json.load(open(fake_loop_json))
    BASE_URL = f"http://localhost:{settings.server_port}"  # Базовый URL вашего FastAPI сервера
    FAKE_PATH = "/gsi/hud"  # Путь, который вы хотите использовать
    INTERVAL_MS = 110

    loop_thread = None
    stop_event = threading.Event()

    async def fake_requests_loop(self):
        async with httpx.AsyncClient(base_url=self.BASE_URL) as client:
            loop_data = deque(self.fake_loop_list)
            while not self.stop_event.is_set():
                if constants.fake_loop_enabled:
                    data = loop_data.popleft()
                    loop_data.append(data)
                    await client.post(self.FAKE_PATH, json=data)
                await asyncio.sleep(self.INTERVAL_MS / 1000)

    def start(self):
        print("FAKE LOOP START")
        self.loop_thread = threading.Thread(
            target=lambda: asyncio.run(self.fake_requests_loop()),
            daemon=True,
        )
        self.loop_thread.start()

    def stop(self):
        print("FAKE LOOP STOP")
        self.stop_event.set()
        self.loop_thread.join(timeout=1)
        self.stop_event.clear()

fake_loop = FakeLoop()