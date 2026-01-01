"""Test load Bible module."""

import pytest
from pythonbible import convert_references_to_verse_ids, get_references

from bibletools._verse_text_map import convert_reference_to_verse_text
from tests.conftest import VERSE_TEXTS


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
