"""Test load Bible module."""

import pytest
from pythonbible import convert_references_to_verse_ids, get_references

from tests.conftest import VERSE_TEXTS


def test_verse_text_mapping_has_all_verses(bible_dict):
    """Test that the parse_xml_to_verse_text_mapping function correctly
    converts a Bible XML string to a dictionary with all verses."""
    assert len(bible_dict) == 31102


@pytest.mark.parametrize("verse_reference, expected_text", VERSE_TEXTS.items())
def test_verse_text_mapping_text(bible_dict, verse_reference, expected_text):
    """Test that the mapping created by parse_xml_to_verse_text_mapping
    correctly maps verse references to their text."""
    verse_id = convert_references_to_verse_ids(
        get_references(verse_reference)
    )[0]
    assert bible_dict[verse_id] == expected_text
