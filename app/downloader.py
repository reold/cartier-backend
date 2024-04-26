from pydeezer import Deezer, Downloader as PydeezerDownloader
from pydeezer.constants import track_formats
from pydeezer.ProgressHandler import BaseProgressHandler

import requests

from abc import ABC, abstractmethod

ARL = "f493d48afc20dac7d9f78888036384c4a67a19ba0500e97958a10e48d86fb53cb3f4719cae5354642a7a8c3ffa01636e1a1209adeb86ea352db4172c35a3468cab61c33136e0cb008c7ee1abc25f82791342943e62d4596ff0f628948e2832e5"

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
