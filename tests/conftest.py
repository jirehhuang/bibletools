"""Shared test fixtures."""

import pytest

from bibletools._utils import _parse_xml_to_dict, _read_file_as_string


@pytest.fixture(scope="session", name="bible_dict")
def fixture_bible_dict():
    """Return the KJV Bible XML as a nested dictionary."""
    xml = _read_file_as_string(file_location="KJV.xml")
    return _parse_xml_to_dict(xml=xml)
