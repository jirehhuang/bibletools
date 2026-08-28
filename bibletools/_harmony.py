"""Gospel harmony cross-references.

For a verse in one of the four Gospels (Matthew, Mark, Luke, John), this
module identifies which "harmony of the Gospels" narrative event(s) that
verse belongs to, and the corresponding parallel passages in the other
Gospels.
"""

import functools
import importlib.resources
import json
from dataclasses import dataclass

from pythonbible import (
    Book,
    NormalizedReference,
    convert_reference_to_verse_ids,
    convert_verse_ids_to_references,
)

from ._parse_references import parse_references
from ._utils import check_valid_verse_ids

HARMONY_DATA_FILE = "harmony.json"

GOSPEL_BOOKS = frozenset({Book.MATTHEW, Book.MARK, Book.LUKE, Book.JOHN})


@dataclass(frozen=True)
class HarmonyEntry:
    """A single Gospel harmony narrative event entry.

    Attributes
    ----------
    category
        The broad narrative category this event falls under, e.g.
        "Ministry and Parables". May be ``None`` for uncategorized entries.
    subject
        A short description of the narrative event, e.g. "The sermon on
        the mount".
    references : tuple[NormalizedReference, ...]
        The resolved parallel passage(s) for this event across the
        Gospels.
    """

    category: str | None
    subject: str
    references: tuple[NormalizedReference, ...]


def _resolve_harmony_references(
    raw_references: list[str],
) -> tuple[NormalizedReference, ...]:
    """Resolve a harmony entry's raw reference strings.

    Parameters
    ----------
    raw_references
        Raw reference strings, e.g. ``["Matthew 5:15;6:22-23"]``.

    Returns
    -------
    tuple[pythonbible.NormalizedReference, ...]
        The resolved references. Whole-book references with no
        chapter/verse (e.g. a bare ``"Matthew"``) are excluded, since they
        do not identify a specific passage.
    """
    return tuple(
        reference
        for raw_reference in raw_references
        for reference in parse_references(raw_reference)
        if reference.start_chapter is not None
        and reference.start_verse is not None
    )


@functools.lru_cache(maxsize=1)
def _load_harmony_entries() -> tuple[HarmonyEntry, ...]:
    """Load and parse the Gospel harmony dataset.

    Returns
    -------
    tuple[HarmonyEntry, ...]
        All harmony entries with at least one resolved reference.
    """
    with (
        importlib.resources.files("bibletools.data")
        .joinpath(HARMONY_DATA_FILE)
        .open("r", encoding="utf-8") as harmony_file
    ):
        raw_entries = json.load(harmony_file)

    entries = (
        HarmonyEntry(
            category=raw_entry["category"],
            subject=raw_entry["subject"],
            references=_resolve_harmony_references(raw_entry["references"]),
        )
        for raw_entry in raw_entries
    )
    return tuple(entry for entry in entries if entry.references)


@functools.lru_cache(maxsize=1)
def _load_harmony_verse_id_index() -> (
    dict[Book, tuple[tuple[HarmonyEntry, frozenset[int]], ...]]
):
    """Index harmony entries by Gospel book, with resolved verse ID sets.

    Returns
    -------
    dict[pythonbible.Book, tuple[tuple[HarmonyEntry, frozenset[int]], ...]]
        Mapping from Gospel book to that book's harmony entries, each
        paired with the set of verse IDs its references in that book
        cover.
    """
    index: dict[Book, list[tuple[HarmonyEntry, frozenset[int]]]] = {
        book: [] for book in GOSPEL_BOOKS
    }
    for entry in _load_harmony_entries():
        references_by_book: dict[Book, list[NormalizedReference]] = {}
        for reference in entry.references:
            references_by_book.setdefault(reference.book, []).append(reference)
        for book, references in references_by_book.items():
            verse_ids = frozenset(
                verse_id
                for reference in references
                for verse_id in convert_reference_to_verse_ids(reference)
            )
            index[book].append((entry, verse_ids))

    return {book: tuple(entries) for book, entries in index.items()}


def get_harmony_entries_for_verse(verse_id: int) -> list[HarmonyEntry]:
    """Return Gospel harmony entries that include the given verse.

    Parameters
    ----------
    verse_id
        The canonical verse ID to look up.

    Returns
    -------
    list[HarmonyEntry]
        The harmony entries whose reference ranges include this verse, in
        dataset order. Empty if `verse_id` is not in one of the four
        Gospels (Matthew, Mark, Luke, John), or if it is in a Gospel but
        not covered by the harmony dataset.
    """
    check_valid_verse_ids([verse_id])

    reference = convert_verse_ids_to_references([verse_id])[0]
    if reference.book not in GOSPEL_BOOKS:
        return []

    return [
        entry
        for entry, verse_ids in _load_harmony_verse_id_index()[reference.book]
        if verse_id in verse_ids
    ]
