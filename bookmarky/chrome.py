import json
import os
import pathlib

from typing import Union, Optional, Generator, List, Type

from bookmarky import browser


class ChromeProfile(browser.BrowserProfile):
    def __init__(self, name:str, path:pathlib.Path, metadata:dict=None):
        super().__init__(name, path)
        if metadata:
            self.display_name = metadata.get("name")
            self.user = metadata.get("user_name")
        else:
            self.display_name = self.name
            self.user = None

    def bookmarks(self) -> Generator[browser.Bookmark, None, None]:
        def gen_folder(parent:str, folder:dict) -> Generator[browser.Bookmark, None, None]:
            path = parent + "/" + folder["name"]
            for child in folder["children"]:
                if "children" in child:
                    yield from gen_folder(path, child)
                else:
                    #   {
                    #   "date_added": "13249994125100809",
                    #   "guid": "13bde0a9-fbf0-485c-a0dd-cc88596cbb9a",
                    #   "id": "6",
                    #   "name": "Example",
                    #   "type": "url",
                    #   "url": "https://example.org/"
                    #   }
                    bm = browser.Bookmark(
                        profile = self,
                        path = path,
                        title = child["name"],
                        url = child["url"],
                        uuid = child["guid"],
                        added = self.conv_webkit_timestamp(child.get("date_added")),
                        modified = self.conv_webkit_timestamp(child.get("date_modified")),
                    )
                    yield bm

        bf = self.path / "Bookmarks"
        with open(bf) as f:
            b = json.loads(f.read())
        root = b["roots"]
        if "bookmark_bar" in root:
            yield from gen_folder("", root["bookmark_bar"])
        if "other" in root:
            yield from gen_folder("", root["other"])


class GoogleChrome(browser.BrowserBase):
    def __init__(self, base_dir:Optional[Union[str,pathlib.Path]]=None, profile:Optional[Type[ChromeProfile]]=None):
        super().__init__(base_dir or self._base_dir())
        self.profile = profile or ChromeProfile

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

    def profiles(self) -> Generator[browser.BrowserProfile, None, None]:
        state_file = self.base_dir / "Local State"
        if state_file.exists():
            with open(state_file) as f:
                state = json.loads(f.read())
            for n, p in state["profile"]["info_cache"].items():
                yield self.profile(n, self.base_dir / n, p)
        else:
            for p in self._find_profiles():
                yield self.profile(p.name, p)


class VivaldiProfile(ChromeProfile):
    pass

class Vivaldi(GoogleChrome):
    def __init__(self, base_dir:Optional[Union[str,pathlib.Path]]=None):
        super().__init__(base_dir, profile=VivaldiProfile)

    def _base_dir(self, name:str=None):
        if name:
            return super()._base_dir(name)
        else:
            for channel in ("vivaldi",):
                p = self._config_dir() / channel
                if p.is_dir():
                    return p

class BraveProfile(ChromeProfile):
    pass

class Brave(GoogleChrome):
    def __init__(self, base_dir:Optional[Union[str,pathlib.Path]]=None):
        super().__init__(base_dir, profile=BraveProfile)

    def _base_dir(self, name:str=None):
        if name:
            return super()._base_dir(name)
        else:
            return self._config_dir() / "BraveSoftware" / "Brave-Browser"

# vim: set et sw=4 ts=4: