"""Load and convert Bible XML files."""

import re
from xml.etree import ElementTree

from pythonbible import (
    Book,
    NormalizedReference,
    convert_reference_to_verse_ids,
    get_verse_id,
)


def _get_book_from_text(text: str) -> Book:
    """Return the Book enum corresponding to a book name or abbreviation.

    Parameters
    ----------
    text
        Book name, abbreviation, or other accepted identifier.

    Returns
    -------
    pythonbible.Book

    Raises
    ------
    ValueError
        If no matching Book is found.
    """
    normalized = text.strip()

    # 1. Enum member name (GENESIS, SAMUEL_1, etc.)
    try:
        return Book[normalized.upper()]
    except KeyError:
        pass

    # 2. Exact title match (case-insensitive)
    for book in Book:
        if normalized.lower() == book.title.lower():
            return book

    # 3. Abbreviation match
    for book in Book:
        if normalized.lower() in (abbr.lower() for abbr in book.abbreviations):
            return book

    # 4. Regex match (most flexible, last resort)
    for book in Book:
        if re.fullmatch(
            book.regular_expression, normalized, flags=re.IGNORECASE
        ):
            return book

    raise ValueError(f"Unknown Bible book: {text!r}")


# pylint: disable=too-many-locals
def parse_xml_to_verse_text_map(
    xml: str,
    testament_path: str | None = None,
    book_spec: tuple[str, str] = ("b", "n"),
    chapter_spec: tuple[str, str] = ("c", "n"),
    verse_spec: tuple[str, str] = ("v", "n"),
) -> dict:
    """Convert a Bible XML string to a nested dictionary.

    Structure:

    {
      verse_id (int): text (str),
    }

    Parameters
    ----------
    xml
        XML content as a string.

    Returns
    -------
    dict
        Dictionary of verse IDs and their corresponding text.
    """
    root = ElementTree.fromstring(xml)
    verse_text_map = {}

    testaments = (
        [root] if testament_path is None else root.findall(testament_path)
    )
    for testament in testaments:

        book_path, book_attrib = book_spec
        for book in testament.findall(book_path):
            book_name = book.attrib[book_attrib]
            book_instance = _get_book_from_text(book_name)

            chapter_path, chapter_attrib = chapter_spec
            for chapter in book.findall(chapter_path):
                chapter_name = chapter.attrib[chapter_attrib]

                verse_path, verse_attrib = verse_spec
                for verse in chapter.findall(verse_path):
                    verse_name = verse.attrib[verse_attrib]

                    verse_id = get_verse_id(
                        book=book_instance,
                        chapter=int(chapter_name),
                        verse=int(verse_name),
                    )
                    verse_text_map[verse_id] = (verse.text or "").strip()

    return verse_text_map


def convert_reference_to_verse_text(
    reference: NormalizedReference,
    verse_text_map: dict[int, str],
    verse_separator: str = " ",
) -> str:
    """Return verse texts for the given reference.

    Parameters
    ----------
    reference
        Reference with verses to retrieve.
    verse_text_map
        Map for verse IDs to their corresponding text values.
    verse_separator
        Separator to use between verse texts.

    Returns
    -------
    str
        Concatenated verse texts corresponding to the given reference.
    """
    verse_ids = convert_reference_to_verse_ids(reference=reference)
    verse_texts = [verse_text_map[vid] for vid in verse_ids]
    return verse_separator.join(verse_texts)
