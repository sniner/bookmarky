import configparser
import json
import os
import pathlib
import sqlite3

from typing import Union, Optional, Generator, List

from bookmarky import browser


class FirefoxProfile(browser.BrowserProfile):
    def __init__(self, name:str, path:pathlib.Path, metadata:dict=None):
        super().__init__(name, path)
        self.display_name = self.name
        self.user = None

    def bookmarks(self) -> Generator[browser.Bookmark, None, None]:
        db_path = self.path / "places.sqlite"
        db = sqlite3.connect(db_path.as_uri()+"?mode=ro", uri=True)
        db.row_factory = sqlite3.Row

        def query(statement:str) -> Generator[dict, None, None]:
            c = db.execute(statement)
            for row in c.fetchall():
                yield dict(row)
            c.close()

        def get_folders() -> Generator[dict, None, None]:
            yield from query("SELECT id, parent, title FROM moz_bookmarks WHERE fk IS NULL")
        
        def get_bookmarks() -> Generator[dict, None, None]:
            yield from query("SELECT b.*, p.url FROM moz_bookmarks b JOIN moz_places p on p.id=b.fk WHERE fk IS NOT NULL")

        try:
            folders = {}
            paths = {}
            for f in get_folders():
                folders[f["id"]] = f
            for folder in folders.values():
                parent = folder["parent"]
                path = [folder["id"]]
                while parent>0:
                    path.append(parent)
                    parent_folder = folders[parent]
                    parent = parent_folder["parent"]
                path_str = "/".join([folders[p]["title"] or "" for p in reversed(path)])
                paths[folder["id"]] = path_str

            for item in get_bookmarks():
                bm = browser.Bookmark(
                    profile = self,
                    path = paths[item["parent"]],
                    title = item["title"],
                    url = item["url"],
                    uuid = item["guid"],
                    added = self.conv_firefox_timestamp(item["dateAdded"]),
                    modified = self.conv_firefox_timestamp(item["lastModified"]),
                )
                yield bm
        finally:
            db.close()




    # def _bookmarks(self) -> Generator[browser.Bookmark, None, None]:
    #     def gen_folder(parent:str, folder:dict) -> Generator[browser.Bookmark, None, None]:
    #         path = parent + "/" + folder["name"]
    #         for child in folder["children"]:
    #             if "children" in child:
    #                 yield from gen_folder(path, child)
    #             else:
    #                 #   {
    #                 #   "date_added": "13249994125100809",
    #                 #   "guid": "13bde0a9-fbf0-485c-a0dd-cc88596cbb9a",
    #                 #   "id": "6",
    #                 #   "name": "Example",
    #                 #   "type": "url",
    #                 #   "url": "https://example.org/"
    #                 #   }
    #                 bm = browser.Bookmark(
    #                     profile = self,
    #                     path = path,
    #                     title = child["name"],
    #                     url = child["url"],
    #                     uuid = child["guid"],
    #                     added = self.conv_webkit_timestamp(child.get("date_added")),
    #                     modified = self.conv_webkit_timestamp(child.get("date_modified")),
    #                 )
    #                 yield bm

    #     bf = self.path / "Bookmarks"
    #     with open(bf) as f:
    #         b = json.loads(f.read())
    #     root = b["roots"]
    #     if "bookmark_bar" in root:
    #         yield from gen_folder("", root["bookmark_bar"])
    #     if "other" in root:
    #         yield from gen_folder("", root["other"])

    def __str__(self):
        return f"FirefoxProfile: '{self.display_name}' -> {self.path}"


class Firefox(browser.BrowserBase):
    def __init__(self, base_dir:Optional[Union[str,pathlib.Path]]=None):
        super().__init__(base_dir or self._base_dir())

    def _base_dir(self, name:str=None):
        if name:
            return self._config_dir() / name
        else:
            m = self._config_dir() / ".mozilla"
            if not m.exists():
                m = pathlib.Path.home() / ".mozilla"
            return m / "firefox"

    def _find_profiles(self) -> List[pathlib.Path]:
        return [p for p in pathlib.Path.iterdir(self.base_dir)
                  if p.is_dir() and (p / "places.sqlite").exists()]

    def profiles(self) -> Generator[browser.BrowserProfile, None, None]:
        state_file = self.base_dir / "profiles.ini"
        if state_file.exists():
            state = configparser.ConfigParser()
            with open(state_file) as f:
                state.read_file(f)
            for sec in state.sections():
                s = dict(state.items(sec))
                if "path" in s:
                    p = self.base_dir / s["path"] if s.get("isrelative")=="1" else pathlib.Path(s["path"]).resolve()
                    yield FirefoxProfile(s["name"], p)
        else:
            for p in self._find_profiles():
                yield FirefoxProfile(p.name, p)


# vim: set et sw=4 ts=4:
