"""Module with utility functions."""

import importlib.resources as pkg_resources
import io
import os
import urllib.parse
import urllib.request


def _read_file_as_string(file_location: str) -> str:
    """Read the content of a file from a local path or URL as a string."""
    if urllib.parse.urlparse(file_location).scheme in ("http", "https"):
        with urllib.request.urlopen(file_location) as response:
            return response.read().decode("utf-8")

    if os.path.isfile(file_location):
        with io.open(file_location, "r", encoding="utf-8") as f:
            return f.read()

    if (
        pkg_resources.files("bibletools.data.translations")
        .joinpath(file_location)
        .is_file()
    ):
        with (
            pkg_resources.files("bibletools.data.translations")
            .joinpath(file_location)
            .open("r", encoding="utf-8") as f
        ):
            return f.read()

    raise FileNotFoundError(f"Unable to read file: {file_location}")
