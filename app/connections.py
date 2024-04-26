import spotipy
from pysondb import PysonDB

from concurrent.futures import ThreadPoolExecutor

db = PysonDB("db.json")

spotify_auth = spotipy.SpotifyClientCredentials()
spotify = spotipy.Spotify(auth_manager=spotify_auth)

executor = ThreadPoolExecutor(2, "deezer downloaders")
