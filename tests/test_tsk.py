"""Test the tsk module."""

import re

import pytest
import pythonbible as pb

from bibletools._tsk import get_tsk_cross_references

EXPECTED_JOHN_3_16_ENTRY_COUNT = 3
EXPECTED_GENESIS_1_13_ENTRY_COUNT = 0
INVALID_VERSE_ID = 99999999


def _verse_id(reference: str) -> int:
    """Return the verse ID for a single-verse reference string."""
    return pb.convert_references_to_verse_ids(pb.get_references(reference))[0]


def test_get_tsk_cross_references_for_john_3_16():
    """Test that get_tsk_cross_references() returns the expected TSK
    entries for John 3:16, a well-known verse."""
    entries = get_tsk_cross_references(_verse_id("John 3:16"))

    assert len(entries) == EXPECTED_JOHN_3_16_ENTRY_COUNT
    assert [entry.word for entry in entries] == [
        "God",
        "gave",
        "that whosoever",
    ]


def test_get_tsk_cross_references_resolves_reference_targets():
    """Test that get_tsk_cross_references() resolves each cross-reference
    target to a NormalizedReference rather than a raw string."""
    entries = get_tsk_cross_references(_verse_id("John 3:16"))
    god_entry = entries[0]

    assert god_entry.word == "God"
    assert god_entry.references[0] == pb.NormalizedReference(
        book=pb.Book.LUKE,
        start_chapter=2,
        start_verse=14,
        end_chapter=2,
        end_verse=14,
        end_book=pb.Book.LUKE,
    )
    assert all(
        isinstance(reference, pb.NormalizedReference)
        for reference in god_entry.references
    )


def test_get_tsk_cross_references_expands_abbreviated_book_names():
    """Test that get_tsk_cross_references() expands TSK-abbreviated
    cross-reference book names (e.g. "1jo") to full resolved books."""
    entries = get_tsk_cross_references(_verse_id("John 3:16"))
    god_entry = entries[0]

    assert any(
        reference.book == pb.Book.JOHN_1 for reference in god_entry.references
    )


def test_get_tsk_cross_references_for_verse_with_no_entries():
    """Test that get_tsk_cross_references() returns an empty list, not an
    error, for a valid verse ID that has no TSK entries."""
    entries = get_tsk_cross_references(_verse_id("Genesis 1:13"))
    assert not entries


def test_error_if_get_tsk_cross_references_with_invalid_verse_id():
    """Test that get_tsk_cross_references() raises a ValueError for an
    invalid verse ID."""
    msg = re.escape("Invalid verse ID(s):")
    with pytest.raises(ValueError, match=msg):
        get_tsk_cross_references(INVALID_VERSE_ID)
