"""Test parse references module."""

import pytest
import pythonbible as pb

from bibletools._parse_references import parse_references

TEXT_EXPECTED_CASES = [
    (
        # Single verse
        "note on 1 John 3:20",
        "1 John 3:20",
    ),
    (
        # Range of verses within a chapter
        "note on Hebrews 9:11-12",
        "Hebrews 9:11-12",
    ),
    (
        # Range of verses across chapters, with trailing dash
        "note on Genesis 17:26-18:2 - Nothing is too hard for God",
        "Genesis 17:26-18:2",
    ),
    (
        # Comma and/or semi-colon separating references to different chapters
        # of a single book, with extra spaces
        "Job 1:6 , 12 , 21-22 ; 2:6-7",
        "Job 1:6,12,21-22,2:6-7",
    ),
    (
        # Book with only 1 chapter
        "note on Jude 3-4 - Grace liberates us",
        "Jude 3-4",
    ),
    (
        # Book with only 1 chapter with chapter number included
        "please see Obadiah 1:3-4 for more details",
        "Obadiah 3-4",
    ),
    (
        # Another example of range across chapters with trailing dash
        "note on Song of Solomon 5:16-6:1 - Jesus will ultimately",
        "Song of Solomon 5:16-6:1",
    ),
    (
        # Partial verses should be treated as whole
        "note on Ecclesiastes 2:24-26a - If we neglect",
        "Ecclesiastes 2:24-26",
    ),
    (
        # Trailing number (footnote) after reference separated by space
        "work of God in Christ ( 1 Corinthians 15:55 7 )",
        "1 Corinthians 15:55",
    ),
    (
        # Many verses, some only separated by spaces
        (
            "Romans 16:20 1 Corinthians 1:3 / 1 Corinthians 16:23 "
            "2 Corinthians 1:2"
        ),
        "Romans 16:20;1 Corinthians 1:3,16:23;2 Corinthians 1:2",
    ),
    (
        # Backwards range with invalid start (1 John 2:35 does not exist)
        "please turn to 1 John 2:35-1 where",
        "",
    ),
    (
        # Separated by semicolon with additional whitespace
        "(see 2 Corinthians 6:18 - 7:1 ; 13:2 ; ",
        "2 Corinthians 6:18-7:1,13:2",
    ),
]


TEXT_EXPECTED_FAILING_CASES = [
    (
        # Invalid range (Ephesians 5:34 does not exist, but 5:33 does)
        "(See Ephesians 5:33-34 ;",
        "Ephesians 5:33",
    ),
    (
        # Invalid backwards range
        "please turn to 1 Peter 3:15-1 where",
        "1 Peter 3:15",
    ),
    (
        # The second Ecclesiastes is not part of a range
        # Additionally, should appear in order of appearance
        (
            "note on 2 Corinthians 4:7-8 - The Christian life; "
            "From the note on Ecclesiastes 1:14 - Ecclesiastes was written"
        ),
        "2 Corinthians 4:7-8;Ecclesiastes 1:14",
    ),
    (
        # Reference to chapter only should be skipped
        "even stronger in 2 Corinthians 9: It is the grace of God",
        "",
    ),
    (
        # Reference order should be preserved as in original text
        "Revelation 22:1-3 and Genesis 22:1-3",
        "Revelation 22:1-3;Genesis 22:1-3",
    ),
]


@pytest.mark.parametrize("text, expected", TEXT_EXPECTED_CASES)
def test_parse_references(text, expected):
    """Test that the parse_references function correctly parses references
    from example sentences."""
    parsed = parse_references(text)
    formatted = pb.format_scripture_references(parsed)
    assert formatted == expected


@pytest.mark.xfail(
    reason=("Known failures in parse_references"),
    strict=True,
)
@pytest.mark.parametrize("text, expected", TEXT_EXPECTED_FAILING_CASES)
def test_parse_references_failures(text, expected):
    """Test that the parse_references function correctly parses references
    from example sentences."""
    parsed = parse_references(text)
    formatted = pb.format_scripture_references(parsed)
    assert formatted == expected
