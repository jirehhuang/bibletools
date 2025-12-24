"""Test utilities module."""

from pathlib import Path

import pytest

from bibletools._utils import _parse_xml_to_dict, _read_file_as_string

KJV_XML_URL = (
    "https://raw.githubusercontent.com/rwev/bible/refs/heads/master/bible/"
    "translations/KJV.xml"
)
KJBIBLE_XML_URL = (
    "https://raw.githubusercontent.com/Beblia/Holy-Bible-XML-Format/"
    "refs/heads/master/EnglishKJBible.xml"
)

VERSE_TEXTS = {
    "Psalm 16:11": (
        "Thou wilt shew me the path of life: in thy presence is fulness "
        "of joy; at thy right hand there are pleasures for evermore."
    ),
    "Ephesians 2:8": (
        "For by grace are ye saved through faith; and that not of "
        "yourselves: it is the gift of God:"
    ),
    "Philippians 1:21": "For to me to live is Christ, and to die is gain.",
    "Proverbs 18:17": (
        "He that is first in his own cause seemeth just; but his "
        "neighbour cometh and searcheth him."
    ),
}


@pytest.mark.parametrize(
    "file_location",
    [
        KJV_XML_URL,
        KJBIBLE_XML_URL,
        "KJV.xml",
        (
            str(
                Path(__file__).resolve().parents[1]
                / "bibletools"
                / "data"
                / "translations"
                / "EnglishKJBible.xml"
            )
        ),
    ],
)
def test_read_file_as_string(file_location):
    """Test that the _read_file_as_string function correctly reads a specified
    file location that could be a URL, file name, or file path."""
    xml = _read_file_as_string(file_location=file_location)
    assert isinstance(xml, str)
    assert xml.startswith("<?xml")
    for verse_text in VERSE_TEXTS.values():
        assert verse_text in xml


@pytest.mark.parametrize(
    "file_location",
    [
        "KJV.xml",
    ],
)
def test_parse_xml_to_dict(file_location):
    """Test that the _parse_xml_to_dict function correctly converts a Bible XML
    string to a nested dictionary."""
    xml = _read_file_as_string(file_location=file_location)
    bible_dict = _parse_xml_to_dict(xml=xml)
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
