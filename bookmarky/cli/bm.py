import csv
import sys

import bookmarky

def bookmark_row(bookmark:bookmarky.Bookmark) -> dict:
    row = dict(bookmark)
    if row["profile"]:
        row["profile"] = bookmark.profile.display_name
        source = bookmark.profile.__class__.__name__
    else:
        source = None
    return {"source": source, **row}

def main():
    browsers = [bookmarky.GoogleChrome, bookmarky.Vivaldi, bookmarky.Brave, bookmarky.Firefox]
    bm_writer = csv.DictWriter(sys.stdout, bookmark_row(bookmarky.Bookmark(None, None, None, None)).keys())
    bm_writer.writeheader()
    for browser_class in browsers:
        browser = browser_class()
        if browser.exists():
            for profile in browser.profiles():
                if profile.exists():
                    for bm in profile.bookmarks():
                        try:
                            bm_writer.writerow(bookmark_row(bm))
                        except BrokenPipeError:
                            exit(0)


if __name__=="__main__":
    main()

# vim: set et sw=4 ts=4: