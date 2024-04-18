from pydeezer import Deezer, Downloader as PydeezerDownloader
from pydeezer.constants import track_formats
import requests

from abc import ABC, abstractmethod

ARL = "a358986cf828cdd3525e8ec4680449e625cf27a8a20e8e248bf579253c4ad529d338fac1a86dc5d29ac7f99f0041e0dab7ad8398b146e91629acb3d9f61792724394982ee96f6e651d96485ea4e8c655bfdadf01415192b411c833d9b215cb06"

class Downloader(ABC):
    @abstractmethod
    def download(isrc: str, directory: str = "."):
        pass

class DeezerDownloader(Downloader):
    def __init__(self):
        self.deezer = Deezer(ARL)

    @staticmethod
    def idFromISRC(isrc: str):
        print("[DeezerDownloaderStatic]: trying to get deezer id")
        response = requests.get(f"https://api.deezer.com/2.0/track/isrc:{isrc}")
        print("[DeezerDownloaderStatic]: Deezer id obtained from isrc", response)

        parsed = response.json()
        return parsed["id"]

    def download(self, isrc: str, directory: str = "."):
        print("[DeezerDownloader]: trying to get deezer id")

        deezer_id = self.idFromISRC(isrc)

        print(f"[DeezerDownloader]: deezer id retrieved, {deezer_id}")

        downloader = PydeezerDownloader(self.deezer, [deezer_id], directory,
                                quality=track_formats.MP3_320, concurrent_downloads=1)
        print("[DeezerDownloader]: Download starting using pydeezer")
        downloader.start()
        print("[DeezerDownloader]: started and probably finished")
