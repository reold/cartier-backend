from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

import subprocess
import signal
import sys

from .connections import executor
from .router import api, hooks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    expose_headers=["x-trackid"],
)

app.include_router(api.router)
app.include_router(hooks.router)


@app.get("/")
async def root():
    return JSONResponse({"success": True, "info": "Reold's Cartier Manager's Server"})


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("assets/favicon.ico")


def reset_handler(*args):

    try: 
        subprocess.run(["rm", "db.json"], check=True)
        subprocess.run(["rm", "-rf", "downloads"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[SHUTDOWN]: deletion error:  {e}")
    except Exception as e:
        print(f"[SHUTDOWN]: unexpected error occured: {e}")
    finally:
        executor.shutdown()
        sys.exit(0)

app.add_event_handler("shutdown", reset_handler)
signal.signal(signal.SIGINT, reset_handler)
signal.signal(signal.SIGTERM, reset_handler)
