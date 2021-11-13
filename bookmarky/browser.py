import datetime
import json
import os
import pathlib

from typing import Union, Optional, Generator, List


class BrowserBase:
    def __init__(self, base_dir:Union[str,pathlib.Path]):
        self.base_dir = pathlib.Path(base_dir)

    @staticmethod
    def _config_dir() -> pathlib.Path:
        if "XDG_CONFIG_HOME" in os.environ:
            conf = pathlib.Path(os.environ["XDG_CONFIG_HOME"])
        else:
            conf = pathlib.Path.home() / ".config"
        return conf

    def exists(self) -> bool:
        return self.base_dir.exists()


class BrowserProfile:
    def __init__(self, name:str, path:pathlib.Path):
        self.path = path
        self.name = name or path.name

    def exists(self) -> bool:
        return self.path.exists()

    def _conv_timestamp(self, timestamp:Union[str,int], year:int=1970):
        if timestamp:
            ms = int(timestamp)
            if ms>0:
                epoch_start = datetime.datetime(year, 1, 1)
                delta = datetime.timedelta(microseconds=ms)
                return epoch_start + delta
        return None

    def conv_webkit_timestamp(self, timestamp:Union[str,int]):
        # The Webkit time value is microseconds from an epoch of 1601-01-01T00:00:00Z
        # https://stackoverflow.com/a/57948727
        return self._conv_timestamp(timestamp, year=1601)

    def conv_firefox_timestamp(self, timestamp:Union[str,int]):
        return self._conv_timestamp(timestamp, year=1970)

    def __str__(self):
        return f"{self.__class__.__name__}: '{self.name}' -> {self.path}"


class Bookmark:
    def __init__(self,
            profile:Optional[BrowserProfile],
            path:Optional[str],
            title:Optional[str],
            url:Optional[str],
            uuid:Optional[str]=None,
            added:Optional[datetime.datetime]=None,
            modified:Optional[datetime.datetime]=None):
        self.profile = profile
        self.path = path
        self.title = title
        self.url = url
        self.uuid = uuid
        self.added = added
        self._modified = None

    @property
    def modified(self) -> datetime.datetime:
        return self._modified or self.added

    @modified.setter
    def modified(self, timestamp:Optional[datetime.datetime]):
        self._modified = modified

    def __iter__(self):
        yield "profile", self.profile
        yield "path", self.path
        yield "title", self.title
        yield "url", self.url
        yield "uuid", self.uuid
        yield "added", self.added
        yield "modified", self.modified

    def __str__(self):
        return f"{self.profile.__class__.__name__}[{self.profile.display_name}]: {self.path}: '{self.title}' -> {self.url}"
