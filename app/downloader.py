from pydeezer import Deezer, Downloader as PydeezerDownloader
from pydeezer.constants import track_formats
from pydeezer.ProgressHandler import BaseProgressHandler

from pysaavn.api import PySaavn

import requests
import os

from abc import ABC, abstractmethod

ARL = "d0b1858de8856ae866dbb1cb21c0e88bc4f042c3614c645b697c151635f504d6355bb75fb02db58af51ff869db055f686d631e7cd644825ca7a7d4a3dd7312f1d42dbbff70dfd6ffebafeb0dd7d689b67673cf96f6b96a756bb527f1c8dc6619"

class Downloader(ABC):
    @abstractmethod
    def download(isrc: str, directory: str = "."):
        pass

class ProgressHandler(BaseProgressHandler):
        def __init__(self):
            self.tracks = []

        def initialize(self, iterable, track_title, track_quality, total_size, chunk_size, **kwargs):

            # fix for printing "downloaded 1 track" instead of 0
            self.tracks.append(kwargs["track_id"])

            self.id = kwargs["track_id"]
            self.iterable = iterable
            self.title = track_title
            self.quality = track_quality
            self.total_size = total_size
            self.chunk_size = chunk_size
            self.size_downloaded = 0
            self.current_chunk_size = 0

        def update(self, *args, **kwargs):
            self.current_chunk_size = kwargs["current_chunk_size"]
            self.size_downloaded += self.current_chunk_size

            progress = self.size_downloaded / self.total_size * 100

            # print(f"{progress}% done")

        def close(self, *args, **kwargs):
            pass

        def close_progress(self):
            pass

class DeezerDownloader(Downloader):
    def __init__(self):
        self.deezer = Deezer(ARL)

    @staticmethod
    def idFromISRC(isrc: str):
        response = requests.get(f"https://api.deezer.com/2.0/track/isrc:{isrc}")

        parsed = response.json()
        return parsed["id"]

    def download(self, isrc: str, directory: str = "."):
        deezer_id = self.idFromISRC(isrc)

        progress_handler = ProgressHandler()
        downloader = PydeezerDownloader(self.deezer, [deezer_id], directory,
                                quality=track_formats.MP3_320, concurrent_downloads=1, progress_handler=progress_handler)
        downloader.start()

class SaavnDownloader(Downloader):
    def __init__(self):
        self.saavn = PySaavn()

    def download(self, name: str, artist: str = "", directory: str="."):
        resp = self.saavn.query(f"{name} {artist}")

        if len(resp) < 1:
            return Exception("song not found")
        
        song = resp[0]

        url_to_file(song.media_url, f"{directory}/{name}.mp3")

def url_to_file(url: str, path: str):
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as file:
            for chunk in resp.iter_content(chunk_size=8192): 
                file.write(chunk)
    
    return path
