from fastapi import FastAPI
from fastapi.responses import HTMLResponse,FileResponse

import os
from dotenv import load_dotenv


# load_dotenv(".env")

app = FastAPI()
# downloader = spotdownloader(os.environ.get("SPOTIPY_CLIENT_ID"), 
#                             os.environ.get("SPOTIPY_CLIENT_SECRET"), 
#                             os.environ.get("GENIUS_CLIENT_TOKEN"),
#                             directory=OUTPUT_FOLDER)


@app.get("/d")
async def root(link: str):
    # if not downloader.validate_playlist_url(link):
    #     return HTMLResponse("invalid playlist url",status_code=404)

    # downloader.start_downloader(link)
    print("downloading link", link)


    return "done"


@app.get("/env/{name}")
def getenv(name: str):
    return os.getenv(name)
