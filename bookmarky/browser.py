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


class BrowserProfile:
    def __init__(self, name:str, path:pathlib.Path):
        self.path = path
        self.name = name or path.name

    def conv_webkit_timestamp(self, timestamp):
        # The Webkit time value is microseconds from an epoch of 1601-01-01T00:00:00Z
        # https://stackoverflow.com/a/57948727
        if timestamp:
            ms = int(timestamp)
            if ms>0:
                epoch_start = datetime.datetime(1601, 1, 1)
                delta = datetime.timedelta(microseconds=ms)
                return epoch_start + delta
        return None

    def conv_firefox_timestamp(self, timestamp):
        if timestamp:
            ms = int(timestamp)
            epoch_start = datetime.datetime(1970, 1, 1)
            delta = datetime.timedelta(microseconds=ms)
            return epoch_start + delta
        return None

    def __str__(self):
        return f"BrowserProfile: '{self.name}' -> {self.path}"


class Bookmark:
    def __init__(self, profile, path, title, url, uuid=None, added=None, modified=None):
        self.profile = profile
        self.path = path
        self.title = title
        self.url = url
        self.uuid = uuid
        self.added = added
        self.modified = modified or self.added

    def __str__(self):
        return f"{self.profile.__class__.__name__}[{self.profile.display_name}]: {self.path}: '{self.title}' -> {self.url}"
