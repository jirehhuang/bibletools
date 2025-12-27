"""Shared test fixtures."""

import pytest

from bibletools._load_bible import _parse_xml_to_dict
from bibletools._utils import _read_file_as_string

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


@pytest.fixture(scope="session", name="bible_dict")
def fixture_bible_dict():
    """Return the KJV Bible XML as a nested dictionary."""
    xml = _read_file_as_string(file_location="KJV.xml")
    return _parse_xml_to_dict(xml=xml)
