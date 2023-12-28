from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from spotify_dl.spotify_dl import spotify_dl
import spotipy

import os, sys, shutil
from uuid import uuid1 as uuid


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

spotify_auth = spotipy.SpotifyClientCredentials()

spotify = spotipy.Spotify(auth_manager=spotify_auth)

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.ico")

@app.get("/")
async def root():
    return "Hello, world!"

@app.get("/user")
async def user(username: str):

    try:
        user_info = spotify.user(username)
        playlist_info = spotify.user_playlists(username)
    except spotipy.exceptions.SpotifyException as e:
        return JSONResponse({"success": False, "info": "spotify error", "msg": e.msg}, status_code=404)

    return {"data": {"user": user_info, "playlists": playlist_info}, "success": True}

@app.get("/playlist")
async def playlist(id: str):

    try:
        playlist_info = spotify.playlist(id)
    except spotipy.exceptions.SpotifyException as e:
        return JSONResponse({"success": False, "info": "spotify error", "msg": e.msg}, status_code=404)

    return playlist_info

@app.get("/track")
async def download_track(link: str, unique_code: str = "", create: bool = False):

    if create:
        unique_code = uuid().hex

    sys.argv = [sys.argv[0], "-l", link, "-o", f"./downloads/{unique_code}"]
    
    try:
        spotify_dl()
    except:
        return JSONResponse({"success": False, "info": "track couldn't be downloaded"}, status_code=404)

    songs = os.listdir(f"./downloads/{unique_code}/")

    return JSONResponse({"success": True, "data": {"unique_code": unique_code, "count": len(songs)}})


@app.get("/stream")
async def stream(unique_code: str, background_tasks: BackgroundTasks):

    unique_folder_path = f"./downloads/{unique_code}"
    
    if not os.path.exists(unique_folder_path):
        return JSONResponse({"success": False, "info": "unique resource doesn't exist"}, status_code=404)
    
    folders = os.listdir(f"{unique_folder_path}")

    if len(folders) == 0:
        return JSONResponse({"success": False, "info": "no resource to stream"}, status_code=404)

    f_folder_name = folders[0]
    song_name = os.listdir(f"{unique_folder_path}/{f_folder_name}")[0]


    song_path = f"{unique_folder_path}/{f_folder_name}/{song_name}"

    file_response = FileResponse(song_path)
    
    background_tasks.add_task(pop_unique_cache, song_path, unique_folder_path, f_folder_name)

    return file_response

def pop_unique_cache(song_path, unique_folder_path, folder_name):
    os.remove(song_path)

    if len(os.listdir(f"{unique_folder_path}/{folder_name}")) == 0:
        shutil.rmtree(f"{unique_folder_path}/{folder_name}")
    
    if len(os.listdir(unique_folder_path)) == 0:
        shutil.rmtree(unique_folder_path)