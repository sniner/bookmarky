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

class ChromeProfile(BrowserProfile):
    def __init__(self, name:str, path:pathlib.Path, metadata:dict=None):
        super().__init__(name, path)
        if metadata:
            self.display_name = metadata.get("name")
            self.user = metadata.get("user_name")
        else:
            self.display_name = self.name
            self.user = None

    def bookmarks(self):
        def gen_folder(parent, folder, acc):
            path = parent + "/" + folder["name"]
            for child in folder["children"]:
                if "children" in child:
                    gen_folder(path, child, acc)
                else:
                    #   {
                    #   "date_added": "13249994125100809",
                    #   "guid": "13bde0a9-fbf0-485c-a0dd-cc88596cbb9a",
                    #   "id": "6",
                    #   "name": "Example",
                    #   "type": "url",
                    #   "url": "https://example.org/"
                    #   }
                    bm = Bookmark(
                        profile = self,
                        path = path,
                        title = child["name"],
                        url = child["url"],
                        uuid = child["guid"],
                        added = self.conv_webkit_timestamp(child.get("date_added")),
                        modified = self.conv_webkit_timestamp(child.get("date_modified")),
                    )
                    acc.append(bm)
            return acc

        bf = self.path / "Bookmarks"
        with open(bf) as f:
            b = json.loads(f.read())
        root = b["roots"]
        if "bookmark_bar" in root:
            bm = gen_folder("", root["bookmark_bar"], [])
        else:
            bm = []
        if "other" in root:
            bm = gen_folder("", root["other"], bm)
        return bm

    def __str__(self):
        return f"ChromeProfile: '{self.display_name}' -> {self.path}"


class GoogleChrome(BrowserBase):
    def __init__(self, base_dir:Union[str,pathlib.Path]):
        super().__init__(base_dir or self._base_dir())

    def _base_dir(self, name:str=None):
        if name:
            return self._config_dir() / name
        else:
            for channel in ("google-chrome", "google-chrome-beta", "google-chrome-unstable"):
                p = self._config_dir() / channel
                if p.is_dir():
                    return p

    def _find_profiles(self) -> List[pathlib.Path]:
        return [p for p in pathlib.Path.iterdir(self.base_dir)
                  if p.is_dir() and (p / "Bookmarks").exists()]

    def profiles(self) -> Generator[BrowserProfile, None, None]:
        state_file = self.base_dir / "Local State"
        if state_file.exists():
            with open(state_file) as f:
                state = json.loads(f.read())
            for n, p in state["profile"]["info_cache"].items():
                yield ChromeProfile(n, self.base_dir / n, p)
        else:
            for p in self._find_profiles():
                yield ChromeProfile(p.name, p)


def main():
    gc = GoogleChrome(base_dir=None)
    print(gc.base_dir)
    for p in gc.profiles():
        print(p)
        for bm in p.bookmarks():
            print(bm, bm.modified)


if __name__=="__main__":
    main()

# vim: set et sw=4 ts=4: