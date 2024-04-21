from pydeezer import Deezer, Downloader as PydeezerDownloader
from pydeezer.constants import track_formats
import requests

from abc import ABC, abstractmethod

ARL = "f493d48afc20dac7d9f78888036384c4a67a19ba0500e97958a10e48d86fb53cb3f4719cae5354642a7a8c3ffa01636e1a1209adeb86ea352db4172c35a3468cab61c33136e0cb008c7ee1abc25f82791342943e62d4596ff0f628948e2832e5"

class Downloader(ABC):
    @abstractmethod
    def download(isrc: str, directory: str = "."):
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

        downloader = PydeezerDownloader(self.deezer, [deezer_id], directory,
                                quality=track_formats.MP3_320, concurrent_downloads=1)
        downloader.start()
