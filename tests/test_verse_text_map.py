"""Test load Bible module."""

import pytest
from pythonbible import Book, convert_references_to_verse_ids, get_references

from bibletools._verse_text_map import (
    VerseTextMapError,
    _get_book_from_number,
    _get_book_from_text,
    convert_reference_to_verse_text,
    parse_xml_to_verse_text_map,
)
from tests.conftest import VERSE_TEXTS

EXPECTED_TOTAL_VERSE_COUNT = 31102


def test_get_book_from_text():
    """Test that _get_book_from_text() correctly maps book names to Book
    instances with various pathways."""
    # Exact Enum name
    assert _get_book_from_text("GENESIS") == Book.GENESIS
    assert _get_book_from_text("CORINTHIANS_1") == Book.CORINTHIANS_1

    # Exact title
    assert _get_book_from_text("Revelation") == Book.REVELATION
    assert _get_book_from_text("1 Timothy") == Book.TIMOTHY_1

    # Abbreviation
    assert _get_book_from_text("Obad") == Book.OBADIAH
    assert _get_book_from_text("1 Pt") == Book.PETER_1
    assert _get_book_from_text("SOS") == Book.SONG_OF_SONGS

    # Regex match
    assert _get_book_from_text("the book of Leviticus") == Book.LEVITICUS

    # Regex matches to the first book in canonical order
    assert _get_book_from_text("Revelation and Genesis") == Book.GENESIS

    # Unknown book
    with pytest.raises(ValueError, match="Unknown Bible book:"):
        _get_book_from_text("Unknown book")


@pytest.mark.parametrize(
    "number, expected_book",
    [
        ("1", Book.GENESIS),
        ("40", Book.MATTHEW),
        ("66", Book.REVELATION),
    ],
)
def test_get_book_from_number(number, expected_book):
    """Test that _get_book_from_number() correctly maps canonical book
    numbers to Book instances."""
    assert _get_book_from_number(number) == expected_book


def test_error_if_get_book_from_number_is_non_numeric():
    """Test that _get_book_from_number() raises a ValueError when given a
    non-numeric book identifier."""
    with pytest.raises(ValueError, match="Non-numeric book identifier:"):
        _get_book_from_number("Genesis")


def test_error_if_get_book_from_number_is_out_of_range():
    """Test that _get_book_from_number() raises a ValueError when given a
    book number with no corresponding Book."""
    with pytest.raises(ValueError, match="Unresolvable book number:"):
        _get_book_from_number("9999")


def test_verse_text_map_has_all_verses(verse_text_map):
    """Test that the parse_xml_to_verse_text_map function correctly
    converts a Bible XML string to a dictionary with all verses."""
    assert len(verse_text_map) == EXPECTED_TOTAL_VERSE_COUNT


def test_verse_text_map_numeric_books_has_all_verses(
    verse_text_map_numeric_books,
):
    """Test that parse_xml_to_verse_text_map() correctly converts a
    testament-nested Bible XML string using numeric book identifiers to a
    dictionary with all verses."""
    assert len(verse_text_map_numeric_books) == EXPECTED_TOTAL_VERSE_COUNT


@pytest.mark.parametrize("verse_reference, expected_text", VERSE_TEXTS.items())
def test_verse_text_map_text(verse_text_map, verse_reference, expected_text):
    """Test that the mapping created by parse_xml_to_verse_text_map
    correctly maps verse references to their text."""
    verse_id = convert_references_to_verse_ids(
        get_references(verse_reference)
    )[0]
    assert verse_text_map[verse_id] == expected_text


@pytest.mark.parametrize("verse_reference, expected_text", VERSE_TEXTS.items())
def test_verse_text_map_numeric_books_text(
    verse_text_map_numeric_books, verse_reference, expected_text
):
    """Test that parse_xml_to_verse_text_map() with numeric book
    identifiers produces the same verse text as the name-based format for
    known verses."""
    verse_id = convert_references_to_verse_ids(
        get_references(verse_reference)
    )[0]
    assert verse_text_map_numeric_books[verse_id] == expected_text


@pytest.mark.parametrize("verse_reference, expected_text", VERSE_TEXTS.items())
def test_convert_reference_to_verse_text_with_single_verse(
    verse_text_map, verse_reference, expected_text
):
    """Test that convert_reference_to_verse_text returns the correct verse text
    for a single verse reference."""
    verse_text = convert_reference_to_verse_text(
        get_references(verse_reference)[0],
        verse_text_map,
    )
    assert verse_text == expected_text


@pytest.mark.parametrize(
    "xml, expected_message",
    [
        (
            '<bible><b n="Genesis"><c n="1"><v n="1">Text</v>',
            "Malformed or unsafe Bible translation XML:",
        ),
        (
            '<bible><b><c n="1"><v n="1">Text</v></c></b></bible>',
            "Book element is missing identifier attribute",
        ),
        (
            '<bible><b n="Genesis"><c><v n="1">Text</v></c></b></bible>',
            "Chapter element is missing identifier attribute",
        ),
        (
            '<bible><b n="Genesis"><c n="1"><v>Text</v></c></b></bible>',
            "Verse element is missing identifier attribute",
        ),
        (
            '<bible><b n="Genesis"><c n="one"><v n="1">Text</v>'
            "</c></b></bible>",
            "Non-numeric chapter attribute: 'one'.",
        ),
        (
            '<bible><b n="Genesis"><c n="1"><v n="one">Text</v>'
            "</c></b></bible>",
            "Non-numeric verse attribute: 'one'.",
        ),
        (
            '<bible><b n="Not A Book"><c n="1"><v n="1">Text</v>'
            "</c></b></bible>",
            "Unknown Bible book: 'Not A Book'",
        ),
        (
            '<bible><b n="Genesis"><c n="1"><v n="1">   </v></c></b>'
            "</bible>",
            "Missing verse text for Genesis 1:1.",
        ),
        (
            '<?xml version="1.0"?>'
            "<!DOCTYPE bible [<!ENTITY xxe SYSTEM "
            '"file:///etc/passwd">]>'
            '<bible><b n="Genesis"><c n="1"><v n="1">&xxe;</v></c>'
            "</b></bible>",
            "Malformed or unsafe Bible translation XML:",
        ),
    ],
)
def test_error_if_parse_xml_to_verse_text_map_with_invalid_xml(
    xml, expected_message
):
    """Test that parse_xml_to_verse_text_map() raises a VerseTextMapError
    with a specific message for each kind of malformed or unsafe input."""
    with pytest.raises(VerseTextMapError, match=expected_message):
        parse_xml_to_verse_text_map(xml=xml)


def test_error_if_parse_xml_to_verse_text_map_with_unresolvable_book_number():
    """Test that parse_xml_to_verse_text_map() raises a VerseTextMapError
    when a numeric book identifier does not correspond to a known book."""
    xml = '<bible><b n="9999"><c n="1"><v n="1">Text</v></c></b></bible>'
    with pytest.raises(VerseTextMapError, match="Unresolvable book number:"):
        parse_xml_to_verse_text_map(xml=xml, book_id_is_numeric=True)


def test_convert_reference_to_verse_text_with_multiple_verses(verse_text_map):
    """Test that convert_reference_to_verse_text returns the correct verse text
    for a reference with multiple verses."""
    verse_text = convert_reference_to_verse_text(
        get_references("Psalm 23")[0],
        verse_text_map,
    )
    assert verse_text == (
        "The LORD is my shepherd; I shall not want. "
        "He maketh me to lie down in green pastures: "
        "he leadeth me beside the still waters. "
        "He restoreth my soul: he leadeth me in the paths of righteousness "
        "for his name's sake. "
        "Yea, though I walk through the valley of the shadow of death, "
        "I will fear no evil: for thou art with me; "
        "thy rod and thy staff they comfort me. "
        "Thou preparest a table before me in the presence of mine enemies: "
        "thou anointest my head with oil; my cup runneth over. "
        "Surely goodness and mercy shall follow me all the days of my life: "
        "and I will dwell in the house of the LORD for ever."
    )
