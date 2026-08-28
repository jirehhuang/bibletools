"""Test the harmony module."""

import re

import pytest
import pythonbible as pb

from bibletools._harmony import get_harmony_entries_for_verse

EXPECTED_MATTHEW_5_15_ENTRY_COUNT = 2
INVALID_VERSE_ID = 99999999


def _verse_id(reference: str) -> int:
    """Return the verse ID for a single-verse reference string."""
    return pb.convert_references_to_verse_ids(pb.get_references(reference))[0]


def test_get_harmony_entries_for_matthew_5_15():
    """Test that get_harmony_entries_for_verse() returns exactly the known
    harmony entries for Matthew 5:15."""
    entries = get_harmony_entries_for_verse(_verse_id("Matthew 5:15"))

    assert len(entries) == EXPECTED_MATTHEW_5_15_ENTRY_COUNT
    assert {entry.subject for entry in entries} == {
        "The sermon on the mount",
        "The light of the body",
    }


def test_get_harmony_entries_resolves_reference_targets():
    """Test that get_harmony_entries_for_verse() resolves each parallel
    passage to a NormalizedReference rather than a raw string."""
    entries = get_harmony_entries_for_verse(_verse_id("Matthew 5:15"))
    sermon_entry = next(
        entry
        for entry in entries
        if entry.subject == "The sermon on the mount"
    )

    assert sermon_entry.category == "Ministry and Parables"
    assert (
        pb.NormalizedReference(
            book=pb.Book.LUKE,
            start_chapter=6,
            start_verse=17,
            end_chapter=6,
            end_verse=49,
            end_book=pb.Book.LUKE,
        )
        in sermon_entry.references
    )


@pytest.mark.parametrize(
    "reference, expected_subject",
    [
        ("Matthew 7:29", "The sermon on the mount"),
        ("Matthew 8:1", "Healing a leper"),
    ],
)
def test_get_harmony_entries_range_boundary(reference, expected_subject):
    """Test that get_harmony_entries_for_verse() correctly includes a verse
    just inside a multi-verse harmony range and excludes it just outside,
    at the exact boundary of "The sermon on the mount" (Matthew 5:1-7:29)."""
    entries = get_harmony_entries_for_verse(_verse_id(reference))
    assert [entry.subject for entry in entries] == [expected_subject]


def test_get_harmony_entries_for_non_gospel_verse_is_empty():
    """Test that get_harmony_entries_for_verse() returns an empty list, not
    an error, for a verse outside the four Gospels."""
    entries = get_harmony_entries_for_verse(_verse_id("Genesis 1:1"))
    assert entries == []


def test_error_if_get_harmony_entries_for_verse_with_invalid_verse_id():
    """Test that get_harmony_entries_for_verse() raises a ValueError for an
    invalid verse ID."""
    msg = re.escape("Invalid verse ID(s):")
    with pytest.raises(ValueError, match=msg):
        get_harmony_entries_for_verse(INVALID_VERSE_ID)
