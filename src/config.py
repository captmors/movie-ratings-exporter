import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import Field 
from pydantic_settings import BaseSettings


ROOT_DIR = Path(__file__).resolve().parent.parent
TMP_DIR = ROOT_DIR / "tmp"
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"

IMDB_RATINGS_PATH = DATA_DIR / "imdb.csv"
KINOPOISK_RATINGS_PATH = ROOT_DIR / "kinopoisk_ratings_parser" / "data.csv"


TMP_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

IMDB_RATINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
KINOPOISK_RATINGS_PATH.parent.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    COOKIES_FOR_CRITICKER: List[Dict[str, str]] = []
    COOKIES_FOR_TASTE_IO:  List[Dict[str, str]] = []

    class Config:
        env_file = ROOT_DIR / ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Automatically add domain/path to the cookies if missing
        self._add_domain_and_path(self.COOKIES_FOR_CRITICKER)
        self._add_domain_and_path(self.COOKIES_FOR_TASTE_IO)

    def _add_domain_and_path(self, cookies: List[Dict[str, str]]):
        if cookies:
            for cookie in cookies:
                if 'domain' not in cookie:
                    cookie['domain'] = '.criticker.com'
                if 'path' not in cookie:
                    cookie['path'] = '/'
                
    

config = Settings()

COOKIES_LIST = config.COOKIES_FOR_CRITICKER + config.COOKIES_FOR_TASTE_IO
