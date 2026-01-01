"""Test load Bible module."""

import pytest
from pythonbible import Book, convert_references_to_verse_ids, get_references

from bibletools._verse_text_map import (
    _get_book_from_text,
    convert_reference_to_verse_text,
)
from tests.conftest import VERSE_TEXTS


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


def test_verse_text_map_has_all_verses(verse_text_map):
    """Test that the parse_xml_to_verse_text_map function correctly
    converts a Bible XML string to a dictionary with all verses."""
    assert len(verse_text_map) == 31102


@pytest.mark.parametrize("verse_reference, expected_text", VERSE_TEXTS.items())
def test_verse_text_map_text(verse_text_map, verse_reference, expected_text):
    """Test that the mapping created by parse_xml_to_verse_text_map
    correctly maps verse references to their text."""
    verse_id = convert_references_to_verse_ids(
        get_references(verse_reference)
    )[0]
    assert verse_text_map[verse_id] == expected_text


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
