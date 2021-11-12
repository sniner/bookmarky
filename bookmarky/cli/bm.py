import bookmarky

def main():
    browser = bookmarky.Firefox()
    # browser = bookmarky.GoogleChrome()
    print(browser.base_dir)
    for p in browser.profiles():
        print(p)
        for bm in p.bookmarks():
            print(bm, bm.modified)


if __name__=="__main__":
    main()

# vim: set et sw=4 ts=4: