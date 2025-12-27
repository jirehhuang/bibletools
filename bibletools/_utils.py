"""Module with utility functions."""

import importlib.resources as pkg_resources
import io
import os
import urllib.parse
import urllib.request
from xml.etree import ElementTree

from pythonbible import is_valid_verse_id


def check_valid_verse_ids(verse_ids: list[int]) -> list[int]:
    """Check that all verse IDs in the list are valid.

    Parameters
    ----------
    verse_ids
        List of verse IDs to check.

    Raises
    ------
    ValueError
        If any verse ID in the list is invalid.
    """
    invalid_verse_ids = [
        vid for vid in verse_ids if not is_valid_verse_id(vid)
    ]
    if invalid_verse_ids:
        raise ValueError(
            f"Invalid verse ID(s): {', '.join(map(str, invalid_verse_ids))}."
        )
    return verse_ids


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
        pkg_resources.files("bibletools.data")
        .joinpath(file_location)
        .is_file()
    ):
        with (
            pkg_resources.files("bibletools.data")
            .joinpath(file_location)
            .open("r", encoding="utf-8") as f
        ):
            return f.read()

    raise FileNotFoundError(f"Unable to read file: {file_location}")


# pylint: disable=too-many-locals
def _parse_xml_to_dict(
    xml: str,
    testament_path: str | None = None,
    book_spec: tuple[str, str] = ("b", "n"),
    chapter_spec: tuple[str, str] = ("c", "n"),
    verse_spec: tuple[str, str] = ("v", "n"),
) -> dict:
    """Convert a Bible XML string to a nested dictionary.

    Structure:

    {
      "book_name": {
        chapter_number: {
          verse_number: {
            "text": "Verse text..."
          },
          ...
        },
        ...
      },
      ...
    }

    Parameters
    ----------
    xml
        XML content as a string.

    Returns
    -------
    dict
        Nested dictionary of books, chapters, and verses with text.
    """
    root = ElementTree.fromstring(xml)
    bible_dict = {}

    testaments = (
        [root] if testament_path is None else root.findall(testament_path)
    )
    for testament in testaments:

        book_path, book_attrib = book_spec
        for book in testament.findall(book_path):
            book_name = book.attrib[book_attrib]
            book_dict = {}

            chapter_path, chapter_attrib = chapter_spec
            for chapter in book.findall(chapter_path):
                chapter_name = chapter.attrib[chapter_attrib]
                chapter_dict = {}

                verse_path, verse_attrib = verse_spec
                for verse in chapter.findall(verse_path):
                    verse_name = verse.attrib[verse_attrib]
                    text = (verse.text or "").strip()
                    chapter_dict[verse_name] = {"text": text}

                book_dict[chapter_name] = chapter_dict

            bible_dict[book_name] = book_dict

    return bible_dict
