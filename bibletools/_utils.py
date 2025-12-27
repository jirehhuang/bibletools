"""Utilities for bibletools."""

from pythonbible import is_valid_verse_id


def check_valid_verse_ids(verse_ids: list[int]) -> list[int]:
    """Check that all verse IDs in the list are valid.

    Parameters
    ----------
    verse_ids
        List of verse IDs to check.

    Raises
    ------
    ValueError
        If any verse ID in the list is invalid.
    """
    invalid_verse_ids = [
        vid for vid in verse_ids if not is_valid_verse_id(vid)
    ]
    if invalid_verse_ids:
        raise ValueError(
            f"Invalid verse ID(s): {', '.join(map(str, invalid_verse_ids))}."
        )
    return verse_ids
