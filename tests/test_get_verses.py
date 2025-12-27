"""Test the get_verses module."""

import re

import numpy as np
import pytest

from bibletools._get_verses import (
    get_all_verse_ids,
    get_highest_weighted_verse,
    get_random_verse_id,
    get_random_verse_ids,
    load_verse_counts,
)


@pytest.fixture(scope="module", name="total_verse_counts")
def fixture_total_verse_counts():
    """Return total verse counts."""
    return load_verse_counts()


def test_get_all_verse_ids():
    """Test that get_all_verse_ids() gets all verse IDs."""
    verse_ids = get_all_verse_ids()
    assert len(verse_ids) == 31102


def test_load_verse_counts(total_verse_counts):
    """Test that total verse counts can be successfully loaded."""
    assert total_verse_counts["total"] == 269094


def test_load_verse_counts_for_rc_sproul():
    """Test that verse counts for R.C. Sproul can be successfully loaded."""
    verse_counts = load_verse_counts("R.C. Sproul")
    assert verse_counts["total"] == 114
    assert verse_counts["23006003"] == 3


def test_error_if_load_verse_counts_for_invalid_author():
    """Test that a ValueError is raised when loading verse counts for an
    invalid author."""
    with pytest.raises(KeyError):
        load_verse_counts("This is not a valid Author")


def test_get_random_verse_ids_without_weights():
    """Test that get_random_verse_ids() returns the expected proportion for
    a verse ID without weights."""
    verse_ids = [20016033, 19119071, 2023013, 7011019]
    random_verse_ids = get_random_verse_ids(
        n_verses=10000, verse_ids=verse_ids
    )
    expected_proportion = 1 / len(verse_ids)
    actual_proportion = np.mean(np.array(random_verse_ids) == 20016033)
    assert np.isclose(actual_proportion, expected_proportion, atol=0.01)


def test_get_random_verse_ids_from_all_verses(total_verse_counts):
    """Test that get_random_verse_ids() returns the expected proportion for
    a verse ID without weights."""
    random_verse_ids = get_random_verse_ids(
        n_verses=10000, verse_weights=total_verse_counts
    )
    verse_id = 45008028
    expected_proportion = (
        total_verse_counts[str(verse_id)] / total_verse_counts["total"]
    )
    actual_proportion = np.mean(np.array(random_verse_ids) == verse_id)
    assert np.isclose(actual_proportion, expected_proportion, atol=0.01)


@pytest.mark.parametrize("pad_weight", [0, 10])
def test_get_random_verse_ids_with_weights_and_pad_weight(pad_weight):
    """Test that get_random_verse_ids() returns the expected proportion for
    a verse ID with partially specified weights for verse IDs and optional pad
    weight."""
    verse_ids = [20016033, 19119071]
    verse_weights = {"20016033": 7}  # Only weight for one verse ID
    random_verse_ids = get_random_verse_ids(
        n_verses=10000,
        verse_ids=verse_ids,
        verse_weights=verse_weights,
        pad_weight=pad_weight,
    )
    expected_proportion = (7 + pad_weight) / (7 + pad_weight * len(verse_ids))
    actual_proportion = np.mean(np.array(random_verse_ids) == 20016033)
    assert np.isclose(actual_proportion, expected_proportion, atol=0.01)


def test_get_random_verse_ids_with_duplicate_verse_ids():
    """Test that get_random_verse_ids() gives multiple chances for duplicate
    verse IDs in the input list."""
    verse_ids = [20016033, 20016033, 19119071]
    random_verse_ids = get_random_verse_ids(
        n_verses=10000, verse_ids=verse_ids
    )
    expected_proportion = 2 / len(verse_ids)
    actual_proportion = np.mean(np.array(random_verse_ids) == 20016033)
    assert np.isclose(actual_proportion, expected_proportion, atol=0.01)


def test_error_if_get_random_verse_id_with_invalid_verse_id():
    """Test that get_random_verse_id() raises a ValueError when an invalid
    verse ID is generated."""
    verse_ids = [20016033, 99999999]  # Invalid verse ID
    verse_weights = {"99999999": 100000}  # High weight to force selection

    # Check all verse IDs before sampling since n_verses=1 <= len(verse_ids)
    msg = re.escape("Invalid verse ID(s):")
    with pytest.raises(ValueError, match=msg):
        get_random_verse_id(
            verse_ids=verse_ids,
            verse_weights=verse_weights,
        )

    # Check sampled verse IDs since n_verses=1 > len(verse_ids)
    with pytest.raises(ValueError, match=msg):
        get_random_verse_ids(
            n_verses=3,
            verse_ids=verse_ids,
            verse_weights=verse_weights,
        )


def test_get_highest_weighted_verse():
    """Test that get_highest_weighted_verse() returns the verse ID with the
    highest weight."""
    verse_ids = [20016033, 19119071, 2023013]
    verse_weights = {"20016033": 5, "19119071": 10, "2023013": 7}

    highest_weighted_verse = get_highest_weighted_verse(
        verse_ids=verse_ids,
        verse_weights=verse_weights,
    )
    assert highest_weighted_verse == 19119071


def test_get_default_highest_weighted_verse():
    """Test that get_highest_weighted_verse() by default returns the verse ID
    with the highest weight, which is the verse ID with the highest total
    verse count."""
    assert get_highest_weighted_verse() == 45008028


def test_error_if_get_highest_weighted_verse_with_invalid_verse_id():
    """Test that get_highest_weighted_verse() raises a ValueError when an
    invalid verse ID is given."""
    verse_ids = [20016033, 99999999]  # Invalid verse ID
    verse_weights = {"99999999": 10}

    msg = re.escape("Invalid verse ID(s):")
    with pytest.raises(ValueError, match=msg):
        get_highest_weighted_verse(
            verse_ids=verse_ids, verse_weights=verse_weights
        )
