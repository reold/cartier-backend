from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse

from spotify_dl.spotify_dl import spotify_dl

import os, sys
from uuid import uuid1 as uuid


app = FastAPI()

@app.get("/d")
async def download(link: str):

    unique_code = uuid().hex
    sys.argv = [sys.argv[0], "-l", link, "-o", f"./downloads/{unique_code}"]
    
    try:
        spotify_dl()
    except:
        return JSONResponse({"success": False, "info": "playlist couldn't be downloaded"}, status_code=404)

    folder_name = os.listdir(f"./downloads/{unique_code}")[0]
    songs = os.listdir(f"./downloads/{unique_code}/{folder_name}")

    return JSONResponse({"success": True, "data": {"unique_code": unique_code, "count": len(songs)}})

@app.get("/s")
async def stream(unique_code: str, background_tasks: BackgroundTasks):

    unique_folder_path = f"./downloads/{unique_code}"
    
    if not os.path.exists(unique_folder_path):
        return JSONResponse({"success": False, "info": "unique resource doesn't exist"}, status_code=404)
    
    folder_name = os.listdir(f"{unique_folder_path}")[0]
    songs = os.listdir(f"{unique_folder_path}/{folder_name}")

    if len(songs) == 0:
        return JSONResponse({"success": False, "info": "no resource to stream"}, status_code=404)


    f_song_name = songs[0]
    f_song_path = f"{unique_folder_path}/{folder_name}/{f_song_name}"

    file_response = FileResponse(f_song_path)
    
    background_tasks.add_task(lambda: os.remove(f_song_path))

    return file_response
