"""Test the parse_natural_reference module."""

import pytest
from pythonbible import Book

from bibletools._parse_natural_reference import (
    AmbiguousNaturalReference,
    MatchedNaturalReference,
    UnparseableNaturalReference,
    _match_book_name,
    _normalize_book_input,
    _normalize_natural_number,
    parse_natural_reference,
)

EXPECTED_JOHN_3_16 = MatchedNaturalReference(
    book=Book.JOHN, chapter=3, verse=16
)
EXPECTED_PETER_1_1_2 = MatchedNaturalReference(
    book=Book.PETER_1, chapter=1, verse=2
)


@pytest.mark.parametrize(
    "token, expected_number",
    [
        ("1", 1),
        ("12", 12),
        ("first", 1),
        ("1st", 1),
        ("second", 2),
        ("twelve", 12),
        ("Twelve", 12),
        ("twenty", 20),
    ],
)
def test_normalize_natural_number(token, expected_number):
    """Test that _normalize_natural_number() converts digit strings,
    ordinal words, and spelled-out number words to integers."""
    assert _normalize_natural_number(token) == expected_number


def test_normalize_natural_number_returns_none_for_unparseable_token():
    """Test that _normalize_natural_number() returns None for a token that
    is not a digit string, ordinal word, or number word."""
    assert _normalize_natural_number("not-a-number") is None


@pytest.mark.parametrize(
    "raw_input, expected_normalized",
    [
        ("First Peter", "1 peter"),
        ("1st John", "1 john"),
        ("  Song   of   Solomon  ", "song of solomon"),
        ("Song-of-Solomon", "song of solomon"),
    ],
)
def test_normalize_book_input(raw_input, expected_normalized):
    """Test that _normalize_book_input() lowercases, strips hyphens, and
    substitutes ordinal words for digits."""
    assert _normalize_book_input(raw_input) == expected_normalized


def test_match_book_name_with_exact_match():
    """Test that _match_book_name() resolves an exact book title match."""
    matched_book, candidates = _match_book_name("1 Peter")
    assert matched_book == Book.PETER_1
    assert not candidates


def test_match_book_name_with_unique_prefix_match():
    """Test that _match_book_name() resolves a unique prefix match."""
    matched_book, candidates = _match_book_name("Revelat")
    assert matched_book == Book.REVELATION
    assert not candidates


def test_match_book_name_with_unique_substring_match():
    """Test that _match_book_name() resolves a unique substring match when
    there is no exact or prefix match."""
    matched_book, candidates = _match_book_name("aggai")
    assert matched_book == Book.HAGGAI
    assert not candidates


def test_match_book_name_with_ambiguous_substring_match():
    """Test that _match_book_name() returns candidates when the input is a
    substring of multiple book titles, with no exact or prefix match."""
    matched_book, candidates = _match_book_name("hronicles")
    assert matched_book is None
    assert Book.CHRONICLES_1 in candidates
    assert Book.CHRONICLES_2 in candidates
    assert len(candidates) == 2


def test_match_book_name_with_ambiguous_match():
    """Test that _match_book_name() returns candidates when the input
    matches multiple books."""
    matched_book, candidates = _match_book_name("1")
    assert matched_book is None
    assert Book.PETER_1 in candidates
    assert Book.SAMUEL_1 in candidates
    assert len(candidates) > 1


def test_match_book_name_with_no_match():
    """Test that _match_book_name() returns no match for unrecognized
    book-name input."""
    matched_book, candidates = _match_book_name("Not A Book")
    assert matched_book is None
    assert not candidates


@pytest.mark.parametrize(
    "submitted_reference, expected_result",
    [
        ("1 Peter 1:1", MatchedNaturalReference(Book.PETER_1, 1, 1)),
        ("john 3:16", EXPECTED_JOHN_3_16),
        ("JOHN 3:16", EXPECTED_JOHN_3_16),
        ("  john   3:16 ", EXPECTED_JOHN_3_16),
        ("john chapter 3:16", EXPECTED_JOHN_3_16),
        ("1 peter 1 verse 1", MatchedNaturalReference(Book.PETER_1, 1, 1)),
        (
            "first peter one verse two",
            EXPECTED_PETER_1_1_2,
        ),
        ("first-peter one verse two", EXPECTED_PETER_1_1_2),
    ],
)
def test_parse_natural_reference_matches(submitted_reference, expected_result):
    """Test that parse_natural_reference() correctly resolves valid inputs
    across ordinal-word, number-word, colon, and verbose "verse" keyword
    styles."""
    assert parse_natural_reference(submitted_reference) == expected_result


def test_parse_natural_reference_with_ambiguous_book_colon_style():
    """Test that parse_natural_reference() returns an
    AmbiguousNaturalReference when the book portion matches multiple books
    in colon style input."""
    result = parse_natural_reference("1 1:1")
    assert isinstance(result, AmbiguousNaturalReference)
    assert Book.PETER_1 in result.candidates
    assert Book.SAMUEL_1 in result.candidates


def test_parse_natural_reference_with_ambiguous_book_verbose_style():
    """Test that parse_natural_reference() returns an
    AmbiguousNaturalReference when the book portion matches multiple books
    in verbose "verse" keyword style input."""
    result = parse_natural_reference("1 1 verse 1")
    assert isinstance(result, AmbiguousNaturalReference)
    assert Book.PETER_1 in result.candidates
    assert Book.SAMUEL_1 in result.candidates


@pytest.mark.parametrize(
    "submitted_reference",
    [
        "not a valid reference at all",
        "zzz 1:1",
        "zzz 1 verse 1",
        "john foo verse 2",
        "john verse",
    ],
)
def test_parse_natural_reference_unparseable(submitted_reference):
    """Test that parse_natural_reference() returns an
    UnparseableNaturalReference for input that cannot be resolved to a
    book, chapter, and verse."""
    assert parse_natural_reference(submitted_reference) == (
        UnparseableNaturalReference()
    )
