from pydeezer import Deezer, Downloader as PydeezerDownloader
from pydeezer.constants import track_formats
from pydeezer.ProgressHandler import BaseProgressHandler

from pysaavn.api import PySaavn

import requests
import os

from abc import ABC, abstractmethod

ARL = "b8a217e61a57b23bca1641ef387b1a47a081e21fd9505df78485292d409c3d7e40bb0aad96b5966d6ac9ad020d69ee7f516f981f65c74d6fe21a4317f1f579333bea2b5b47949002478a663ca59bf8bfc17065ea7744d9545353d01a43eca63f"


class Downloader(ABC):
    @abstractmethod
    def download(isrc: str, directory: str = "."):
        pass


class ProgressHandler(BaseProgressHandler):
    def __init__(self):
        self.tracks = []

    def initialize(
        self, iterable, track_title, track_quality, total_size, chunk_size, **kwargs
    ):

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
        downloader = PydeezerDownloader(
            self.deezer,
            [deezer_id],
            directory,
            quality=track_formats.MP3_320,
            concurrent_downloads=1,
            progress_handler=progress_handler,
        )
        downloader.start()


class SaavnDownloader(Downloader):
    def __init__(self):
        self.saavn = PySaavn()

    def temp_download(self, name: str, artist: str = "", directory: str = "."):
        resp = requests.get(
            f"https://saavn.dev/api/search/songs?query={name} by {artist}"
        )
        data = resp.json()

        if len(data["data"]["results"]) == 0:
            return Exception("song not found")

        song = data["data"]["results"][0]
        url = song["downloadUrl"][-1]["url"]

        url_to_file(url, f"{directory}/{name}.mp3")

    def download(self, name: str, artist: str = "", directory: str = "."):
        resp = requests.get(
            f"https://saavn.dev/api/search/songs?query={name} by {artist}"
        )

        data = resp.json()["data"]
        results = data["results"]

        if len(results) == 0:
            return Exception("song not found")

        song = results[0]
        song_token = song["url"].split("/")[-1]

        pysaavn_resp = self.saavn.parse_query(
            self.saavn.session.get(
                self.saavn.domain
                + f"?__call=webapi.get&token={song_token}&type=song&includeMetaTags=0&ctx=wap6dot0&api_version=4&_format=json&_marker=0"
            ).json()["songs"]
        )

        if len(pysaavn_resp) == 0:
            return Exception("localized search failed")

        song = pysaavn_resp[0]

        url_to_file(song.media_url, f"{directory}/{name}.mp3")


def url_to_file(url: str, path: str):
    with requests.get(url, stream=True) as resp:
        resp.raise_for_status()

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "wb") as file:
            for chunk in resp.iter_content(chunk_size=8192):
                file.write(chunk)

    return path
