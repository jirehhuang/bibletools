"""Get verses from the Bible with various methods."""

import importlib.resources
import json
import random
from typing import Mapping

from pythonbible import (
    Book,
    NormalizedReference,
    convert_reference_to_verse_ids,
)

from ._utils import check_valid_verse_ids

VERSE_COUNTS_FILE = "verse-counts-by-author-and-id.json"


def get_all_verse_ids() -> list[int]:
    """Return all verse IDs in the Bible."""
    return list(
        convert_reference_to_verse_ids(
            NormalizedReference(
                book=Book.GENESIS,
                start_chapter=1,
                start_verse=1,
                end_chapter=22,
                end_verse=21,
                end_book=Book.REVELATION,
            )
        )
    )


def load_verse_counts(
    author: str = "total",
) -> dict[str, int]:
    """Load verse counts from a JSON file.

    Parameters
    ----------
    author
        Author name to retrieve counts for. If ``None``, load total counts.

    Returns
    -------
    dict[str, int]
        Dictionary mapping verse IDs to their counts. Note that the keys are
        strings rather than integers corresponding to verse IDs because JSON
        keys must be strings, and the data structure includes a "total" key.
    """
    with (
        importlib.resources.files("bibletools.data")
        .joinpath(VERSE_COUNTS_FILE)
        .open("r", encoding="utf-8") as f
    ):
        verse_counts_by_author = json.load(f)

    return verse_counts_by_author[author]


def get_random_verse_ids(
    n_verses: int = 1,
    verse_ids: list[int] | None = None,
    verse_weights: Mapping[str, int | float] | None = None,
    pad_weight: int | float = 1,
) -> list[int]:
    """Return random verse IDs.

    Parameters
    ----------
    verse_ids
        List of verse IDs to choose from.
    verse_weights
        Dictionary mapping verse IDs to their weights.
    pad_weight
        Padding weight added to the weight of each verse. If a verse ID is not
        in `verse_weights`, it is given a weight of 0 plus the `pad_weight`.
    n_verses
        Number of verses to return.

    Returns
    -------
    list[int]
        List of random verse IDs.
    """
    if verse_ids is None:
        verse_ids = get_all_verse_ids()

    if verse_weights is None:
        verse_weights = {}

    if len(verse_ids) <= n_verses:
        check_valid_verse_ids(verse_ids)

    random_verse_ids = random.choices(
        verse_ids,
        weights=[
            verse_weights.get(str(vid), 0) + pad_weight for vid in verse_ids
        ],
        k=n_verses,
    )

    if n_verses < len(verse_ids):
        check_valid_verse_ids(random_verse_ids)

    return random_verse_ids


def get_random_verse_id(
    verse_ids: list[int] | None = None,
    verse_weights: Mapping[str, int | float] | None = None,
    pad_weight: int | float = 1,
) -> int:
    """Return a single random verse ID.

    Parameters
    ----------
    verse_ids
        List of verse IDs to choose from.
    verse_weights
        Dictionary mapping verse IDs to their weights.
    pad_weight
        Padding weight added to the weight of each verse. If a verse ID is not
        in `verse_weights`, it is given a weight of 0 plus the `pad_weight`.

    Returns
    -------
    int
        A single random verse ID.
    """
    return get_random_verse_ids(
        n_verses=1,
        verse_ids=verse_ids,
        verse_weights=verse_weights,
        pad_weight=pad_weight,
    )[0]


def get_highest_weighted_verse(
    verse_ids: list[int] | None = None,
    verse_weights: Mapping[str, int | float] | None = None,
) -> int:
    """Return the highest weighted verse ID."""
    if verse_ids is None:
        verse_ids = get_all_verse_ids()

    if verse_weights is None:
        verse_weights = load_verse_counts()

    highest_weighted_verse = max(
        verse_ids, key=lambda vid: verse_weights.get(str(vid), 0)
    )
    return check_valid_verse_ids([highest_weighted_verse])[0]
