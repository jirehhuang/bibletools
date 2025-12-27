"""Test load Bible module."""

from tests.conftest import VERSE_TEXTS


def test_parse_xml_to_dict(bible_dict):
    """Test that the _parse_xml_to_dict function correctly converts a Bible XML
    string to a nested dictionary."""
    assert isinstance(bible_dict, dict)
    assert (
        bible_dict["Psalms"]["16"]["11"]["text"] == VERSE_TEXTS["Psalm 16:11"]
    )
    assert (
        bible_dict["Ephesians"]["2"]["8"]["text"]
        == VERSE_TEXTS["Ephesians 2:8"]
    )
    assert (
        bible_dict["Philippians"]["1"]["21"]["text"]
        == VERSE_TEXTS["Philippians 1:21"]
    )
    assert (
        bible_dict["Proverbs"]["18"]["17"]["text"]
        == VERSE_TEXTS["Proverbs 18:17"]
    )
