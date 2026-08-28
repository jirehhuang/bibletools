"""Make data used in bibletools."""

import importlib.resources
import json
import pathlib

from pythonbible import (
    Book,
    convert_references_to_verse_ids,
    get_references,
    get_verse_id,
)

from bibletools._parse_references import parse_references


def make_verse_counts_by_author_and_id():
    """Make verse counts by author and verse ID.

    Function to convert verse counts by verse and author to verse counts by
    author and verse ID.
    """
    # Input structure:
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
                verse_ids = convert_references_to_verse_ids(
                    get_references(f"{book} {chapter}:{verse}")
                )
                if len(verse_ids) < 1:
                    continue  # Skip verse that does not exist
                if len(verse_ids) > 1:
                    print("here")
                verse_id = verse_ids[0]

                for author in verse_counts[book][chapter][verse].keys():
                    count = verse_counts[book][chapter][verse][author]
                    author_ = "total" if author == "count" else author

                    if author_ not in verse_counts_by_author:
                        verse_counts_by_author[author_] = {}
                    verse_counts_by_author[author_][verse_id] = count

    # Sort by totals for each author
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

    # Output structure:
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


TSK_DATA_FILE = "tskxref.txt"
_TSK_DATA_ENCODING = "latin-1"
_TSK_FIELD_COUNT = 6

# Map from TSK dataset book abbreviation to the corresponding Book. This is
# the TSK dataset's own abbreviation scheme (distinct from
# ``Book.abbreviations``) and is required to resolve cross-reference targets
# within each entry's ``references`` field.
TSK_BOOKS: dict[str, Book] = {
    "ge": Book.GENESIS,
    "ex": Book.EXODUS,
    "le": Book.LEVITICUS,
    "nu": Book.NUMBERS,
    "de": Book.DEUTERONOMY,
    "jos": Book.JOSHUA,
    "jud": Book.JUDGES,
    "ru": Book.RUTH,
    "1sa": Book.SAMUEL_1,
    "2sa": Book.SAMUEL_2,
    "1ki": Book.KINGS_1,
    "2ki": Book.KINGS_2,
    "1ch": Book.CHRONICLES_1,
    "2ch": Book.CHRONICLES_2,
    "ezr": Book.EZRA,
    "ne": Book.NEHEMIAH,
    "es": Book.ESTHER,
    "job": Book.JOB,
    "ps": Book.PSALMS,
    "pr": Book.PROVERBS,
    "ec": Book.ECCLESIASTES,
    "so": Book.SONG_OF_SONGS,
    "isa": Book.ISAIAH,
    "jer": Book.JEREMIAH,
    "la": Book.LAMENTATIONS,
    "eze": Book.EZEKIEL,
    "da": Book.DANIEL,
    "ho": Book.HOSEA,
    "joe": Book.JOEL,
    "am": Book.AMOS,
    "ob": Book.OBADIAH,
    "jon": Book.JONAH,
    "mic": Book.MICAH,
    "na": Book.NAHUM,
    "hab": Book.HABAKKUK,
    "zep": Book.ZEPHANIAH,
    "hag": Book.HAGGAI,
    "zec": Book.ZECHARIAH,
    "mal": Book.MALACHI,
    "mt": Book.MATTHEW,
    "mr": Book.MARK,
    "lu": Book.LUKE,
    "joh": Book.JOHN,
    "ac": Book.ACTS,
    "ro": Book.ROMANS,
    "1co": Book.CORINTHIANS_1,
    "2co": Book.CORINTHIANS_2,
    "ga": Book.GALATIANS,
    "eph": Book.EPHESIANS,
    "php": Book.PHILIPPIANS,
    "col": Book.COLOSSIANS,
    "1th": Book.THESSALONIANS_1,
    "2th": Book.THESSALONIANS_2,
    "1ti": Book.TIMOTHY_1,
    "2ti": Book.TIMOTHY_2,
    "tit": Book.TITUS,
    "phm": Book.PHILEMON,
    "heb": Book.HEBREWS,
    "jas": Book.JAMES,
    "1pe": Book.PETER_1,
    "2pe": Book.PETER_2,
    "1jo": Book.JOHN_1,
    "2jo": Book.JOHN_2,
    "3jo": Book.JOHN_3,
    "jude": Book.JUDE,
    "re": Book.REVELATION,
}


def _expand_tsk_reference_token(token: str) -> list[list[int]]:
    """Resolve a single TSK reference token to compact reference tuples.

    Each resolved reference is encoded as a 5-element list of
    ``[book, start_chapter, start_verse, end_chapter, end_verse]`` rather
    than a dict, to keep the precomputed JSON file's size manageable as
    package data.

    Parameters
    ----------
    token
        A single TSK-abbreviated reference, e.g. ``"1ch 16:26"`` or
        ``"ps 33:6,9"``.

    Returns
    -------
    list[list[int]]
        JSON-serializable ``[book, start_chapter, start_verse, end_chapter,
        end_verse]`` lists. Empty if the token could not be resolved.
    """
    token = token.strip()
    if not token or " " not in token:
        return []

    abbreviation, chapter_verse = token.split(" ", 1)
    book = TSK_BOOKS.get(abbreviation.lower())
    if book is None:
        return []

    return [
        [
            reference.book.value,
            reference.start_chapter,
            reference.start_verse,
            reference.end_chapter,
            reference.end_verse,
        ]
        for reference in parse_references(f"{book.title} {chapter_verse}")
    ]


def make_tsk_cross_references_by_id():
    """Precompute TSK cross-references keyed by verse ID.

    Parses the raw ``tskxref.txt`` TSK (Treasury of Scripture Knowledge)
    dataset (tab-separated, abbreviated book/reference notation) once into
    a JSON file keyed by verse ID, so that ``bibletools._tsk`` can look up
    cross-references at runtime without re-parsing reference text (which is
    too slow to redo on every process start) on every import.
    """
    output = {}

    with (
        importlib.resources.files("bibletools.data")
        .joinpath(TSK_DATA_FILE)
        .open("r", encoding=_TSK_DATA_ENCODING) as tsk_file
    ):
        for line in tsk_file:
            fields = line.rstrip("\n").split("\t")
            if len(fields) != _TSK_FIELD_COUNT:
                continue  # Skip malformed lines

            book_key, chapter, verse, _unused, word, references = fields
            verse_id = get_verse_id(
                book=Book(int(book_key)),
                chapter=int(chapter),
                verse=int(verse),
            )

            resolved_references = [
                reference
                for raw_token in references.strip().split(";")
                for reference in _expand_tsk_reference_token(raw_token)
            ]
            output.setdefault(str(verse_id), []).append(
                [word.strip(), resolved_references]
            )

    output_path = (
        pathlib.Path(__file__).parent.parent
        / "bibletools"
        / "data"
        / "tsk-cross-references-by-id.json"
    )
    with output_path.open("w", encoding="utf-8") as out_f:
        json.dump(
            output,
            out_f,
            ensure_ascii=False,
            separators=(",", ":"),
        )


if __name__ == "__main__":
    make_verse_counts_by_author_and_id()
    make_tsk_cross_references_by_id()
