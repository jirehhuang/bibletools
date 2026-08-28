"""Toolkit for working with the Bible."""

from ._get_verses import (
    get_all_verse_ids,
    get_highest_weighted_verse,
    get_random_verse_id,
    get_random_verse_ids,
    load_verse_counts,
)
from ._harmony import GOSPEL_BOOKS, HarmonyEntry, get_harmony_entries_for_verse
from ._parse_natural_reference import (
    AmbiguousNaturalReference,
    MatchedNaturalReference,
    NaturalReferenceResult,
    UnparseableNaturalReference,
    parse_natural_reference,
)
from ._parse_references import parse_references
from ._tsk import TSKCrossReference, get_tsk_cross_references
from ._utils import check_valid_verse_ids, read_file_as_string
from ._verse_text_map import (
    VerseTextMapError,
    convert_reference_to_verse_text,
    parse_xml_to_verse_text_map,
)
