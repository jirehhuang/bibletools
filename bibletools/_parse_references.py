"""Parse Bible references."""

import re

import pythonbible as pb


def _normalize_noncontiguous_separators(text: str) -> str:
    """Replace all non-contiguous verse separators with a standard comma.

    The correct format is, for example: Book 1:2-3, 5, 7-8, 2:1-2

    Semicolons should be replaced with commas within individual books, but
    semicolons separating different books should be preserved.

    Parameters
    ----------
    text
        The input string possibly containing non-contiguous verse separators.

    Returns
    -------
    str
        The string with all non-contiguous verse separators replaced by ','.
    """
    return re.sub(r";(?=\s*\d)", ",", text)


def _normalize_dashes(text: str) -> str:
    """Replace all single-character dash variantswith a standard dash.

    Parameters
    ----------
    text
        The input string possibly containing dash variants.

    Returns
    -------
    str
        The string with all dash variants replaced by '-'.
    """
    dash_variants = [
        "\u2013",  # en dash
        "\u2014",  # em dash
        "\u2012",  # figure dash
        "\u2015",  # horizontal bar
        "\u2212",  # minus sign
        "\uFE58",  # small em dash
        "\uFE63",  # small hyphen-minus
        "\uFF0D",  # fullwidth hyphen-minus
    ]
    for variant in dash_variants:
        text = text.replace(variant, "-")
    return text


def parse_references(text: str) -> list[pb.NormalizedReference]:
    """Parse all compound Bible references from a text.

    Parameters
    ----------
    text
        A sentence containing a compound Bible reference.
    """
    text = _normalize_dashes(text)
    text = _normalize_noncontiguous_separators(text)
    return pb.get_references(text)
