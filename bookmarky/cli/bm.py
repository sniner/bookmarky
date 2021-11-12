import bookmarky

def main():
    gc = bookmarky.Firefox() #.GoogleChrome()
    print(gc.base_dir)
    for p in gc.profiles():
        print(p)
        for bm in p.bookmarks():
            print(bm, bm.modified)


if __name__=="__main__":
    main()

# vim: set et sw=4 ts=4: