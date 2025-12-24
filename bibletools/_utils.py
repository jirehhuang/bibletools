"""Module with utility functions."""

import importlib.resources as pkg_resources
import io
import os
import urllib.parse
import urllib.request


def _read_file_as_string(file_location: str) -> str:
    """Read the content of a file as a string.

    Params
    ------
    file_location
        The location of the file to read. This can be one of the following:

        - A URL to a remote file (http or https).
        - An absolute or relative file path on the local filesystem.
        - A package resource located in `bibletools.data.translations`.

    Returns
    -------
    str
        The content of the file as a string.
    """
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
