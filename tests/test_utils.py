"""Test utilities module."""

from pathlib import Path

import pytest

from bibletools._utils import read_file_as_string
from tests.conftest import VERSE_TEXTS

KJV_XML_URL = (
    "https://raw.githubusercontent.com/rwev/bible/refs/heads/master/bible/"
    "translations/KJV.xml"
)

KJBIBLE_XML_URL = (
    "https://raw.githubusercontent.com/Beblia/Holy-Bible-XML-Format/"
    "refs/heads/master/EnglishKJBible.xml"
)


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
                / "EnglishKJBible.xml"
            )
        ),
    ],
)
def testread_file_as_string(file_location):
    """Test that the read_file_as_string function correctly reads a specified
    file location that could be a URL, file name, or file path."""
    xml = read_file_as_string(file_location=file_location)
    assert isinstance(xml, str)
    assert xml.startswith("<?xml")
    for verse_text in VERSE_TEXTS.values():
        assert verse_text in xml
