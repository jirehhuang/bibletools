"""Treasury of Scripture Knowledge (TSK) cross-references.

The TSK is a public-domain Bible cross-reference dataset: for a given verse,
it lists related/supporting cross-reference verses grouped by the specific
word or phrase in the verse they relate to.

The raw dataset (``tskxref.txt``) uses abbreviated book names and requires
reference-text parsing to resolve; that parsing is too slow to redo on every
process start (tens of thousands of reference strings), so it is done once,
offline, by ``scripts/make_data.py`` (see
``make_tsk_cross_references_by_id()``), which ships its output as the
``tsk-cross-references-by-id.json`` package data file that this module
loads at runtime.
"""

import functools
import importlib.resources
import json
from dataclasses import dataclass

from pythonbible import Book, NormalizedReference

from ._utils import check_valid_verse_ids

TSK_CROSS_REFERENCES_FILE = "tsk-cross-references-by-id.json"


@dataclass(frozen=True)
class TSKCrossReference:
    """A single TSK cross-reference entry for a verse.

    Attributes
    ----------
    word
        The specific word or phrase in the verse the cross-references
        relate to.
    references : tuple[NormalizedReference, ...]
        The resolved cross-reference target(s).
    """

    word: str
    references: tuple[NormalizedReference, ...]


def _reference_from_list(data: list) -> NormalizedReference:
    """Reconstruct a NormalizedReference from its precomputed JSON form.

    Parameters
    ----------
    data
        A ``[book, start_chapter, start_verse, end_chapter, end_verse]``
        list, as produced by ``scripts/make_data.py``.

    Returns
    -------
    pythonbible.NormalizedReference
    """
    book_value, start_chapter, start_verse, end_chapter, end_verse = data
    book = Book(book_value)
    return NormalizedReference(
        book=book,
        start_chapter=start_chapter,
        start_verse=start_verse,
        end_chapter=end_chapter,
        end_verse=end_verse,
        end_book=book,
    )


@functools.lru_cache(maxsize=1)
def _load_tsk_cross_references_by_id() -> (
    dict[str, tuple[TSKCrossReference, ...]]
):
    """Load the precomputed TSK cross-reference lookup table.

    Returns
    -------
    dict[str, tuple[TSKCrossReference, ...]]
        Mapping from verse ID (as a string; see note on JSON-serialized
        verse ID keys in :mod:`bibletools._get_verses`) to that verse's TSK
        cross-reference entries.
    """
    with (
        importlib.resources.files("bibletools.data")
        .joinpath(TSK_CROSS_REFERENCES_FILE)
        .open("r", encoding="utf-8") as tsk_file
    ):
        raw_lookup = json.load(tsk_file)

    return {
        verse_id: tuple(
            TSKCrossReference(
                word=word,
                references=tuple(
                    _reference_from_list(reference) for reference in references
                ),
            )
            for word, references in entries
        )
        for verse_id, entries in raw_lookup.items()
    }


def get_tsk_cross_references(verse_id: int) -> list[TSKCrossReference]:
    """Return TSK cross-reference entries for a single verse.

    Parameters
    ----------
    verse_id
        The canonical verse ID to look up.

    Returns
    -------
    list[TSKCrossReference]
        The verse's TSK cross-reference entries, in dataset order. Empty
        if the verse ID is valid but has no TSK entries (the TSK dataset
        does not cover every verse).
    """
    check_valid_verse_ids([verse_id])

    return list(_load_tsk_cross_references_by_id().get(str(verse_id), ()))
