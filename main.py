from fastapi import FastAPI
from fastapi.responses import FileResponse

import os, sys
from spotify_dl.spotify_dl import spotify_dl

app = FastAPI()


@app.get("/d")
async def root(link: str):

    sys.argv = [sys.argv[0], "-l", link, "-o", "./downloads"]
    
    try:
        spotify_dl()
    except:
        return "failed"

    folder_name = os.listdir("./downloads")[0]
    f_file_name = os.listdir(f"./downloads/{folder_name}")[0]

    return FileResponse(f"./downloads/{folder_name}/{f_file_name}", filename=f_file_name)