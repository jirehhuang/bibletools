"""Test load Bible module."""

import pytest
from pythonbible import convert_references_to_verse_ids, get_references

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
