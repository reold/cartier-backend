from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_socketio import SocketManager

import subprocess

from .comms import SocketHandler
from .connections import executor
from .router import api, hooks

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], expose_headers=["x-trackid"])

app.include_router(api.router)
app.include_router(hooks.router)

sio_manager = SocketManager(app=app, mount_location="/socket.io", cors_allowed_origins=[])
sio_handle = SocketHandler(sio_manager)

@app.get("/")
async def root():
    return JSONResponse({"success": True, "info": "Reold's Cartier Manager's Server"})

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("assets/favicon.ico")

def shutdown_handler():
    subprocess.run(["rm", "db.json"])
    subprocess.run(["rm", "-rf", "downloads"])

    executor.shutdown()

app.add_event_handler("shutdown", shutdown_handler)