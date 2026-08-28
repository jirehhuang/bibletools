"""Parse a single, human-typed natural-language Bible reference guess.

This module addresses a different problem than the prose-reference
extraction in :mod:`bibletools._parse_references`, which extracts
citations embedded in prose text. Here, the input is a single, possibly
malformed, possibly partial reference typed by a user (e.g. as a guess for
a verse's reference in a quiz flow), and the caller needs to know whether
it matched cleanly, matched ambiguously (multiple candidate books), or did
not match at all.

A narrower strict-format fallback regex (``Book 1:1``-style, single-token
book names only) is sometimes used alongside natural-language parsers like
this one. It is intentionally not implemented here: the colon-style handling
in :func:`parse_natural_reference` already supports multi-word book names
(via :func:`_match_book_name`) and is strictly more capable than such a
fallback, so a separate fallback would be redundant.
"""

import re
from dataclasses import dataclass

from pythonbible import Book
from word2number import w2n

_ORDINAL_WORDS: dict[str, str] = {
    "first": "1",
    "1st": "1",
    "one": "1",
    "second": "2",
    "2nd": "2",
    "two": "2",
    "third": "3",
    "3rd": "3",
    "three": "3",
    "fourth": "4",
    "four": "4",
    "fifth": "5",
    "five": "5",
    "sixth": "6",
    "six": "6",
    "seventh": "7",
    "seven": "7",
    "eighth": "8",
    "eight": "8",
    "ninth": "9",
    "nine": "9",
    "tenth": "10",
    "ten": "10",
    "eleventh": "11",
    "eleven": "11",
    "twelfth": "12",
    "twelve": "12",
}


@dataclass(frozen=True)
class MatchedNaturalReference:
    """A natural-language reference that resolved to exactly one verse.

    Attributes
    ----------
    book
        The resolved book.
    chapter
        The resolved chapter number.
    verse
        The resolved verse number.
    """

    book: Book
    chapter: int
    verse: int


@dataclass(frozen=True)
class AmbiguousNaturalReference:
    """A natural-language reference whose book matched multiple candidates.

    Attributes
    ----------
    candidates
        The books that could plausibly match the input's book portion.
    """

    candidates: tuple[Book, ...]


@dataclass(frozen=True)
class UnparseableNaturalReference:
    """A natural-language reference that could not be parsed at all."""


NaturalReferenceResult = (
    MatchedNaturalReference
    | AmbiguousNaturalReference
    | UnparseableNaturalReference
)


def _normalize_natural_number(token: str) -> int | None:
    """Convert a digit string, ordinal word, or number word to an integer.

    Parameters
    ----------
    token
        A single token, e.g. ``"1"``, ``"first"``, or ``"twelve"``.

    Returns
    -------
    int | None
        The parsed integer, or ``None`` if the token could not be parsed
        as a natural number.
    """
    normalized = token.lower().replace("-", " ").strip()
    if normalized in _ORDINAL_WORDS:
        return int(_ORDINAL_WORDS[normalized])
    if normalized.isdigit():
        return int(normalized)
    try:
        return w2n.word_to_num(normalized)
    except ValueError:
        return None


def _normalize_book_input(text: str) -> str:
    """Normalize a book-name input string for matching.

    Lowercases, strips punctuation and hyphens, substitutes ordinal words
    for digits (e.g. "First Peter" -> "1 peter"), and collapses whitespace.

    Parameters
    ----------
    text
        The raw book-name input string.

    Returns
    -------
    str
        The normalized book-name string.
    """
    normalized = text.lower().replace("-", " ").strip()
    normalized = re.sub(r"[^\w\s]", "", normalized)
    for word, digit in _ORDINAL_WORDS.items():
        normalized = re.sub(rf"\b{word}\b", digit, normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _match_book_name(
    text: str,
) -> tuple[Book | None, tuple[Book, ...]]:
    """Match a normalized book-name input against all known Bible books.

    Matching is attempted, in order, as: exact match, unique-prefix match,
    then unique-substring match.

    Parameters
    ----------
    text
        The raw book-name input string.

    Returns
    -------
    tuple[Book | None, tuple[Book, ...]]
        A tuple of (resolved book, candidate books). Exactly one of these
        is populated: if the match is unique, the first element is the
        resolved ``Book`` and the second is empty; if the match is
        ambiguous, the first element is ``None`` and the second contains
        the candidate books; if there is no match at all, both are empty/
        ``None``.
    """
    normalized_input = _normalize_book_input(text)
    book_map = {_normalize_book_input(book.title): book for book in Book}

    if normalized_input in book_map:
        return book_map[normalized_input], ()

    prefix_candidates = tuple(
        book
        for normalized_title, book in book_map.items()
        if normalized_title.startswith(normalized_input)
    )
    if len(prefix_candidates) == 1:
        return prefix_candidates[0], ()
    if len(prefix_candidates) > 1:
        return None, prefix_candidates

    substring_candidates = tuple(
        book
        for normalized_title, book in book_map.items()
        if normalized_input in normalized_title
    )
    if len(substring_candidates) == 1:
        return substring_candidates[0], ()
    if len(substring_candidates) > 1:
        return None, substring_candidates

    return None, ()


_MIN_VERBOSE_TOKEN_COUNT = 2  # at least one book token plus a chapter token


def _resolve_book_match(
    book_raw: str,
) -> Book | AmbiguousNaturalReference | None:
    """Resolve a raw book-name string to a Book, ambiguity, or failure.

    Parameters
    ----------
    book_raw
        The raw, un-normalized book-name portion of the input.

    Returns
    -------
    Book | AmbiguousNaturalReference | None
        The resolved ``Book`` on a unique match, an
        ``AmbiguousNaturalReference`` on multiple candidates, or ``None``
        if there is no match at all.
    """
    matched_book, candidates = _match_book_name(book_raw)
    if candidates:
        return AmbiguousNaturalReference(candidates=candidates)
    return matched_book


def _parse_verbose_style(normalized: str) -> NaturalReferenceResult:
    """Parse the "book chapter verse N" verbose input style.

    Parameters
    ----------
    normalized
        The whitespace/hyphen/colon-normalized, ordinal-substituted input
        string, known to contain the literal word "verse".

    Returns
    -------
    NaturalReferenceResult
        The parsed result.
    """
    book_chapter_part, _, verse_raw = normalized.rpartition("verse")
    tokens = book_chapter_part.strip().split()
    if len(tokens) < _MIN_VERBOSE_TOKEN_COUNT:
        return UnparseableNaturalReference()

    chapter_raw = tokens[-1]
    book_raw = " ".join(tokens[:-1])

    book_result = _resolve_book_match(book_raw)
    if isinstance(book_result, AmbiguousNaturalReference):
        return book_result
    if book_result is None:
        return UnparseableNaturalReference()

    chapter = _normalize_natural_number(chapter_raw)
    verse = _normalize_natural_number(verse_raw.strip())
    if chapter is None or verse is None:
        return UnparseableNaturalReference()

    return MatchedNaturalReference(
        book=book_result, chapter=chapter, verse=verse
    )


def _parse_colon_style(normalized: str) -> NaturalReferenceResult:
    """Parse the "book chapter:verse" colon input style.

    Parameters
    ----------
    normalized
        The whitespace/hyphen/colon-normalized, ordinal-substituted input
        string.

    Returns
    -------
    NaturalReferenceResult
        The parsed result.
    """
    match = re.match(
        r"^(?P<book>.+?) (?P<chapter>\d+):(?P<verse>\d+)$", normalized
    )
    if not match:
        return UnparseableNaturalReference()

    book_result = _resolve_book_match(match.group("book"))
    if isinstance(book_result, AmbiguousNaturalReference):
        return book_result
    if book_result is None:
        return UnparseableNaturalReference()

    return MatchedNaturalReference(
        book=book_result,
        chapter=int(match.group("chapter")),
        verse=int(match.group("verse")),
    )


def parse_natural_reference(text: str) -> NaturalReferenceResult:
    """Parse a single, human-typed natural-language Bible reference guess.

    Supports ordinal words (e.g. "first"), spelled-out numbers (e.g.
    "twelve"), digit strings, a "verse"/"chapter" keyword style (e.g.
    "1 peter 1 verse 1" or "first peter one verse two"), and a colon style
    (e.g. "1 peter 1:1"), all case-insensitively and tolerant of extra
    whitespace and hyphens.

    Parameters
    ----------
    text
        The raw, user-typed reference guess.

    Returns
    -------
    NaturalReferenceResult
        A ``MatchedNaturalReference`` if the input resolved to exactly one
        book/chapter/verse; an ``AmbiguousNaturalReference`` if the book
        portion matched multiple candidate books; or an
        ``UnparseableNaturalReference`` if the input could not be parsed.
    """
    normalized = text.lower().replace("-", " ").strip()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"\s*:\s*", ":", normalized)
    normalized = re.sub(r"\bchapter\b", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    for word, digit in _ORDINAL_WORDS.items():
        normalized = re.sub(rf"\b{word}\b", digit, normalized)

    if "verse" in normalized:
        return _parse_verbose_style(normalized)

    return _parse_colon_style(normalized)
