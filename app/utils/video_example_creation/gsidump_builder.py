import json
from contextlib import asynccontextmanager

import fastapi
import uvicorn

HOST = "localhost"
PORT = 8001
DUMP_PATH = './dump.ndjson'

dump_file = open(DUMP_PATH, 'w')
# gsi_number = 0

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI, *args, **kwargs):
    app.gsi_number = 0
    app.dump_file = open(DUMP_PATH, 'w')
    yield
    app.dump_file.close()

app = fastapi.FastAPI(lifespan=lifespan)

@app.post("/gsi/hud", status_code=200)
async def handle_gsi(request: fastapi.Request):
    js = json.loads(await request.body())
    request.app.gsi_number += 1
    js = js | {"gsi_number": request.app.gsi_number}
    request.app.dump_file.write(json.dumps(js) + "\n")


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)