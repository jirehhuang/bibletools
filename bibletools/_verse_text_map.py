"""Load and convert Bible XML files."""

import re

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
from pythonbible import (
    Book,
    NormalizedReference,
    convert_reference_to_verse_ids,
    get_verse_id,
)


class VerseTextMapError(ValueError):
    """Raised when Bible translation XML cannot be parsed.

    Carries enough detail about the failure (which book/chapter/verse was
    being processed and the raw offending value, if applicable) for callers
    to build a friendly, specific error message for end users, e.g. when
    validating an uploaded translation file.

    Parameters
    ----------
    message
        Human-readable description of the failure.
    book
        Raw book identifier being processed when the failure occurred, if
        known.
    chapter
        Raw chapter identifier being processed when the failure occurred, if
        known.
    verse
        Raw verse identifier being processed when the failure occurred, if
        known.
    raw_value
        The specific offending raw attribute or text value, if applicable.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        message: str,
        *,
        book: str | None = None,
        chapter: str | None = None,
        verse: str | None = None,
        raw_value: str | None = None,
    ) -> None:
        super().__init__(message)
        self.book = book
        self.chapter = chapter
        self.verse = verse
        self.raw_value = raw_value


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
        if re.search(book.regular_expression, normalized, flags=re.IGNORECASE):
            return book

    raise ValueError(f"Unknown Bible book: {text!r}")


def _get_book_from_number(text: str) -> Book:
    """Return the Book enum corresponding to a canonical book number.

    Parameters
    ----------
    text
        Canonical book number (1-66 for the standard Protestant canon,
        matching ``pythonbible.Book`` enum values) as a string.

    Returns
    -------
    pythonbible.Book

    Raises
    ------
    ValueError
        If the text is not a valid integer or does not correspond to a
        known Book.
    """
    try:
        number = int(text.strip())
    except ValueError as error:
        raise ValueError(f"Non-numeric book identifier: {text!r}") from error

    try:
        return Book(number)
    except ValueError as error:
        raise ValueError(f"Unresolvable book number: {text!r}") from error


# pylint: disable=too-many-locals
# pylint: disable=too-many-arguments,too-many-positional-arguments
def parse_xml_to_verse_text_map(  # noqa: PLR0913,PLR0917
    xml: str,
    testament_path: str | None = None,
    book_spec: tuple[str, str] = ("b", "n"),
    chapter_spec: tuple[str, str] = ("c", "n"),
    verse_spec: tuple[str, str] = ("v", "n"),
    book_id_is_numeric: bool = False,
) -> dict:
    """Convert a Bible XML string to a nested dictionary.

    Structure:

    {
      verse_id (int): text (str),
    }

    Supports both known Bible translation XML shapes by way of the
    ``testament_path``, ``book_spec``, ``chapter_spec``, and ``verse_spec``
    parameters: the "flat" format (root ``<bible>`` directly containing book
    elements identified by name/abbreviation) and the "testament-nested"
    format (``<bible>`` containing ``<testament>`` containing ``<book>``
    elements identified by a canonical numeric book identifier).

    This function parses XML using ``defusedxml``, which disables DTD
    processing and external entity resolution. This is a security-relevant
    hardening measure since this function may be used to parse untrusted,
    user-uploaded translation XML files; do not replace it with the
    standard library's ``xml.etree.ElementTree``, which is vulnerable to
    XXE and entity-expansion attacks on untrusted input.

    Parameters
    ----------
    xml
        XML content as a string.
    testament_path
        Path to testament elements, if any, e.g. ``"testament"``. If
        ``None``, book elements are searched for directly under the root
        element.
    book_spec
        Tuple of (element tag, identifier attribute name) for book
        elements, e.g. ``("b", "n")`` or ``("book", "number")``.
    chapter_spec
        Tuple of (element tag, identifier attribute name) for chapter
        elements, e.g. ``("c", "n")`` or ``("chapter", "number")``.
    verse_spec
        Tuple of (element tag, identifier attribute name) for verse
        elements, e.g. ``("v", "n")`` or ``("verse", "number")``.
    book_id_is_numeric
        If ``True``, the book identifier attribute is treated as a
        canonical book number (1-66 for the standard Protestant canon)
        rather than a book name or abbreviation.

    Returns
    -------
    dict
        Dictionary of verse IDs and their corresponding text.

    Raises
    ------
    VerseTextMapError
        If the XML is malformed or otherwise unsafe to parse, or if a
        book/chapter/verse identifier is missing, non-numeric (for
        chapter/verse), or unresolvable (for book), or if a verse is
        missing its text content.
    """
    try:
        root = ElementTree.fromstring(xml)
    except (ElementTree.ParseError, DefusedXmlException) as error:
        raise VerseTextMapError(
            f"Malformed or unsafe Bible translation XML: {error}"
        ) from error

    verse_text_map: dict[int, str] = {}

    testaments = (
        [root] if testament_path is None else root.findall(testament_path)
    )
    book_path, book_attrib = book_spec
    chapter_path, chapter_attrib = chapter_spec
    verse_path, verse_attrib = verse_spec

    for testament in testaments:
        for book in testament.findall(book_path):
            try:
                book_name = book.attrib[book_attrib]
            except KeyError as error:
                raise VerseTextMapError(
                    f"Book element is missing identifier attribute "
                    f"{book_attrib!r}."
                ) from error

            try:
                book_instance = (
                    _get_book_from_number(book_name)
                    if book_id_is_numeric
                    else _get_book_from_text(book_name)
                )
            except ValueError as error:
                raise VerseTextMapError(
                    str(error), book=book_name, raw_value=book_name
                ) from error

            for chapter in book.findall(chapter_path):
                try:
                    chapter_name = chapter.attrib[chapter_attrib]
                except KeyError as error:
                    raise VerseTextMapError(
                        f"Chapter element is missing identifier attribute "
                        f"{chapter_attrib!r}.",
                        book=book_name,
                    ) from error

                try:
                    chapter_number = int(chapter_name)
                except ValueError as error:
                    raise VerseTextMapError(
                        f"Non-numeric chapter attribute: {chapter_name!r}.",
                        book=book_name,
                        chapter=chapter_name,
                        raw_value=chapter_name,
                    ) from error

                for verse in chapter.findall(verse_path):
                    try:
                        verse_name = verse.attrib[verse_attrib]
                    except KeyError as error:
                        raise VerseTextMapError(
                            f"Verse element is missing identifier "
                            f"attribute {verse_attrib!r}.",
                            book=book_name,
                            chapter=chapter_name,
                        ) from error

                    try:
                        verse_number = int(verse_name)
                    except ValueError as error:
                        raise VerseTextMapError(
                            f"Non-numeric verse attribute: {verse_name!r}.",
                            book=book_name,
                            chapter=chapter_name,
                            verse=verse_name,
                            raw_value=verse_name,
                        ) from error

                    verse_text = (verse.text or "").strip()
                    if not verse_text:
                        raise VerseTextMapError(
                            "Missing verse text for "
                            f"{book_instance.title} {chapter_number}:"
                            f"{verse_number}.",
                            book=book_name,
                            chapter=chapter_name,
                            verse=verse_name,
                        )

                    verse_id = get_verse_id(
                        book=book_instance,
                        chapter=chapter_number,
                        verse=verse_number,
                    )
                    verse_text_map[verse_id] = verse_text

    return verse_text_map


# pylint: enable=too-many-arguments,too-many-positional-arguments


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
