import sys
from setuptools import setup, find_packages

setup(
    # Requirements
    python_requires=">=3.9",

    # Metadata
    name = "bookmarky",
    version = "0.1.0",
    author = "Stefan Schönberger",
    author_email = "mail@sniner.dev",
    description = "Export tool for web browser bookmarks",

    # Packages
    packages = find_packages(),

    # Dependencies
    install_requires = [
    ],
    extras_require = {
        "dev": [
        ],
    },

    # Scripts
    entry_points = {
        "console_scripts": [
            "bm = bookmarky.cli.bm:main",
        ]
    },

    # Packaging information
    platforms = "posix",
)

# vim: set et sw=4 ts=4: