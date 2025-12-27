"""Test module to generate and manipulate data."""

import importlib.resources
import json
import pathlib

from pythonbible import (
    convert_references_to_verse_ids,
    get_references,
)


def test_create_verse_counts_by_author():
    """Test to create verse counts by author from previously generated file."""
    # Structure:
    # {
    #   book: {
    #     chapter: {
    #       verse: {
    #         author: count (int),
    #       },
    #     },
    #   },
    # }
    with (
        importlib.resources.files("bibletools.data")
        .joinpath("verse-counts-by-verse-and-author.json")
        .open("r", encoding="utf-8") as f
    ):
        verse_counts = json.load(f)

    verse_counts_by_author = {}

    for book in verse_counts.keys():
        for chapter in verse_counts[book].keys():
            for verse in verse_counts[book][chapter].keys():
                verse_id = convert_references_to_verse_ids(
                    get_references(f"{book} {chapter}:{verse}")
                )[0]
                for author in verse_counts[book][chapter][verse].keys():
                    count = verse_counts[book][chapter][verse][author]
                    author_ = "total" if author == "count" else author
                    if author_ not in verse_counts_by_author:
                        verse_counts_by_author[author_] = {}
                    verse_counts_by_author[author_][verse_id] = count

    for author, counts in verse_counts_by_author.items():
        counts["total"] = sum(counts.values())
        verse_counts_by_author[author] = dict(
            sorted(
                counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

    verse_counts_by_author = dict(
        sorted(
            verse_counts_by_author.items(),
            key=lambda item: item[1]["total"],
            reverse=True,
        )
    )

    # Structure:
    # {
    #   "total": {
    #     "total": count (int),
    #     verse_id: count (int),
    #     ...
    #   },
    #   author: {
    #     "total": count (int),
    #     verse_id: count (int),
    #     ...
    #   },
    #   ...
    # }
    output_path = (
        pathlib.Path(__file__).parent.parent
        / "bibletools"
        / "data"
        / "verse-counts-by-author-and-id.json"
    )
    with output_path.open("w", encoding="utf-8") as out_f:
        json.dump(verse_counts_by_author, out_f, ensure_ascii=False, indent=2)
