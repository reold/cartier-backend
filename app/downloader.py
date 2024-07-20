from pydeezer import Deezer, Downloader as PydeezerDownloader
from pydeezer.constants import track_formats
from pydeezer.ProgressHandler import BaseProgressHandler

import requests

from abc import ABC, abstractmethod

ARL = "d85984fff88e73a2e0ed2021eb1b816a373f84306c371785e162f2895aa5530e5348775fd045d6df62613c843371df072ff4f1150205204d561861ad374809cd8b832108edd428aff69bec881fe4fa080b308631ca2ebab0c890fc7682c98ac9"

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
