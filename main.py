from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from spotify_dl.spotify_dl import spotify_dl
import spotipy
from downloader import DeezerDownloader

from concurrent.futures import ThreadPoolExecutor

import os, sys, shutil
from pysondb import PysonDB
from pysondb import errors as PysonErrors

from dotenv import load_dotenv
load_dotenv()

db = PysonDB("db.json")

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], expose_headers=["x-trackid"])

spotify_auth = spotipy.SpotifyClientCredentials()

spotify = spotipy.Spotify(auth_manager=spotify_auth)

executor = ThreadPoolExecutor(2, "deezer downloaders")
app.add_event_handler("shutdown", lambda: executor.shutdown())

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.ico")

@app.get("/")
async def root():
    return JSONResponse({"success": True})

@app.get("/user")
async def user(username: str):

    try:
        user_info = spotify.user(username)
        playlist_info = spotify.user_playlists(username)
    except spotipy.exceptions.SpotifyException as e:
        return JSONResponse({"success": False, "info": "spotify error", "msg": e.msg}, status_code=404)

    del user_info["href"]
    del user_info["uri"]
    del user_info["type"]

    user_info["followers"] = user_info["followers"]["total"]
    
    user_info["external_url"] = user_info["external_urls"]["spotify"]
    del user_info["external_urls"]

    playlist_info = playlist_info["items"]

    for i in range(len(playlist_info)):
        del playlist_info[i]["collaborative"]
        del playlist_info[i]["primary_color"]
        del playlist_info[i]["public"]
        del playlist_info[i]["snapshot_id"]
        del playlist_info[i]["type"]
        del playlist_info[i]["uri"]
        del playlist_info[i]["tracks"]

        playlist_info[i]["external_url"] = playlist_info[i]["external_urls"]["spotify"]

    resp = {"data": {"user": user_info, "playlists": {"all": playlist_info}}, "success": True}

    return resp

@app.get("/playlist")
async def playlist(id: str):

    try:
        playlist_info = spotify.playlist(id)
    except spotipy.exceptions.SpotifyException as e:
        return JSONResponse({"success": False, "info": "spotify error", "msg": e.msg}, status_code=404)

    playlist_info = playlist_info["tracks"]["items"]
    for i in range(len(playlist_info)):
        playlist_info[i] = playlist_info[i]["track"]
        
        playlist_info[i] = {"images": playlist_info[i]["album"]["images"], "id": playlist_info[i]["id"], "url": playlist_info[i]["external_urls"]["spotify"], "name": playlist_info[i]["name"]}

    return playlist_info

@app.get("/track")
async def download_track(link: str, background_tasks: BackgroundTasks, key: str = "", create: bool = False):

    if create:
        key = db.add({"songs": []})

    song_id = link.split("/")[-1].split("?")[0]

    record = db.get_by_id(key)
    
    db.update_by_id(key, {"songs": [*record["songs"], {"link": link, "id": song_id, "status": "downloading"}]})

    try:
        executor.submit(task_deezer_dl, key, link, song_id)
        # executor.submit(task_spotify_dl, key, link, song_id)
        # background_tasks.add_task(task_spotify_dl, key, link, song_id)
    except:
        return JSONResponse({"success": False, "info": "track couldn't be downloaded"}, status_code=404)


    return JSONResponse({"success": True, "data": {"key": key}})


def task_deezer_dl(key: str, link: str, id: str):
    id_path = f"./downloads/{key}/{id}"
    failed = False

    try:
        spotify_track = spotify.track(link)
        isrc = spotify_track["external_ids"]["isrc"]

        deezer_dl = DeezerDownloader()
        deezer_dl.download(isrc, id_path)
    except:
        failed = True
        shutil.rmtree(f"{id_path}")

    record = db.get_by_id(key)

    for song in record["songs"]:
        if song["id"] == id:
            if failed:
                song["status"] = "failed"
            else:
                song["status"] = "ready"

    db.update_by_id(key, record)
    

def task_spotify_dl(key: str, link: str, id: str):
    id_path = f"./downloads/{key}/{id}"
    failed = False

    sys.argv = [sys.argv[0], "-l", link, "-mc", "2", "-o", id_path]

    try:
        spotify_dl()
        
        song_folder_name = os.listdir(id_path)[0]
        song_name = os.listdir(f"{id_path}/{song_folder_name}")[0]
        song_path = f"{id_path}/{song_folder_name}/{song_name}"


        shutil.move(song_path, f"{id_path}")
        shutil.rmtree(f"{id_path}/{song_folder_name}")
    except:
        failed = True
        shutil.rmtree(f"{id_path}")
    
    record = db.get_by_id(key)

    for song in record["songs"]:
        if song["id"] == id:
            if failed:
                song["status"] = "failed"
            else:
                song["status"] = "ready"

    db.update_by_id(key, record)
    

@app.get("/status")
async def download_status(key: str):

    try:
        record = db.get_by_id(key)
    except PysonErrors.IdDoesNotExistError:
        return JSONResponse({"success": False, "info": "unique resource doesn't exist (db)"}, status_code=404)
                

    return JSONResponse({"success": True, "data": record["songs"]})

@app.get("/stream")
async def stream(key: str, background_tasks: BackgroundTasks):

    await background_tasks()

    unique_folder_path = f"./downloads/{key}"
    
    try:
        record = db.get_by_id(key)
    except PysonErrors.IdDoesNotExistError:
        return JSONResponse({"success": False, "info": "unique resource doesn't exist (db)"}, status_code=404)


    if not record["songs"]:
        return JSONResponse({"success": False, "info": "no resource to stream (db)"}, status_code=404)
        
    f_song_record = record["songs"][0]

    if f_song_record["status"] == "failed":
        
        record["songs"] = [song for song in record["songs"] if song["id"] != f_song_record["id"]]
        db.update_by_id(key, record)

        return JSONResponse({"success": False, "info": "conversion failed"}, status_code=404)


    f_song_folder_name = f_song_record["id"]
    song_files = os.listdir(f"{unique_folder_path}/{f_song_folder_name}")
    song_name = next((file for file in song_files if file.endswith('.mp3')), None)
    song_path = f"{unique_folder_path}/{f_song_folder_name}/{song_name}"

    file_response = FileResponse(song_path, headers={"X-trackid": f_song_folder_name})

    record["songs"] = [song for song in record["songs"] if song["id"] != f_song_record["id"]]

    if len(record["songs"]) == 0:
        db.delete_by_id(key)
    else:
        db.update_by_id(key, record)

    background_tasks.add_task(pop_unique_cache, song_path, unique_folder_path, f_song_folder_name)

    return file_response

def pop_unique_cache(song_path, unique_folder_path, folder_name):
    os.remove(song_path)

    if len(os.listdir(f"{unique_folder_path}/{folder_name}")) == 0:
        shutil.rmtree(f"{unique_folder_path}/{folder_name}")
    
    if len(os.listdir(unique_folder_path)) == 0:
        shutil.rmtree(unique_folder_path)