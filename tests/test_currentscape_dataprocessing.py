"""Test currentscape dataprocessing functions."""

import numpy as np

from currentscape.data_processing import (
    autoscale_ticks_and_ylim,
    sum_chunks,
    check_chunksize,
    remove_zero_arrays,
    reorder,
    order_of_mag,
    round_down_sig_digit,
)


def compare_floats(n1, n2, err=1e-10):
    """Assert that two floats are closer than a given uncertainty."""
    assert (n1 - n2) / n1 < err


def test_order_of_mag():
    """Test function returning order of magnitude of a number."""
    assert order_of_mag(1234) == 1000
    assert order_of_mag(0.0456) == 0.01


def test_round_down_sig_digit():
    """Test function rounding down a number to one (or more) significant digit(s)."""
    assert round_down_sig_digit(0.0456) == 0.04
    assert round_down_sig_digit(723) == 700
    assert round_down_sig_digit(0.5) == 0.5
    assert round_down_sig_digit(1234, 100) == 1200


def test_autoscale():
    """Test autoscale function."""
    config_key = "test"
    test_dict = {"ylim": (0, 0), "ticks": [0, 0]}
    c = {config_key: test_dict}

    max_ = 654321
    autoscale_ticks_and_ylim(c, max_, 0, config_key)

    compare_floats(c[config_key]["ylim"][0], 0.3271605)
    compare_floats(c[config_key]["ylim"][1], 3271605)

    compare_floats(c[config_key]["ticks"][2], 60000)
    compare_floats(c[config_key]["ticks"][1], 600)
    compare_floats(c[config_key]["ticks"][0], 6)

    max_ = 0.723
    autoscale_ticks_and_ylim(c, 0, max_, config_key)

    compare_floats(c[config_key]["ylim"][0], 0.0000003615)
    compare_floats(c[config_key]["ylim"][1], 3.615)

    compare_floats(c[config_key]["ticks"][2], 0.07)
    compare_floats(c[config_key]["ticks"][1], 0.0007)
    compare_floats(c[config_key]["ticks"][0], 0.000007)


def test_sum_chunks():
    """Test reshaping in sum chunks function."""
    arr1 = np.array([1, 1, 2, 2, 3, 3])
    arr2 = np.array([0, 1, 2, 0, 1, 2])
    arr = np.array([arr1, arr2])

    assert np.array_equal(sum_chunks(arr, 1), [[1, 1, 2, 2, 3, 3], [0, 1, 2, 0, 1, 2]])
    assert np.array_equal(sum_chunks(arr, 2), [[1, 2, 3], [0.5, 1, 1.5]])
    assert np.array_equal(sum_chunks(arr, 3), [[4 / 3.0, 8 / 3.0], [1, 1]])


def test_check_chunksize():
    """Test common divisor finder."""
    # chunksize < 1 case
    assert check_chunksize(0, 3000) == 1
    # chunksize > data size case
    assert check_chunksize(3333, 3000) == 3000
    # chunksize divisor of data size case
    assert check_chunksize(50, 3000) == 50
    # chunksize not a divisor of data size case
    assert check_chunksize(49, 3000) == 40


def test_remove_zero_arrays():
    """Test remove zero array function."""
    arr = np.array([np.array([0, 1]), np.array([0, 0]), np.array([np.nan, 0])])
    new_arr, new_idx = remove_zero_arrays(arr)

    assert np.array_equal(new_arr, [[0, 1]])
    assert new_idx == 0


def test_reorder():
    """Test reorder function.

    The function removes null arrays, reorders from largest sum to smallest,
    and returns reordered list and reordered indexes.
    """
    arr1 = np.array([1, 1, 2, 2, 3, 3])
    arr2 = np.array([0, 1, 2, 0, 1, 2])
    arr3 = np.array([0, 0, 0, 0, 0, 0])
    arr4 = np.array([1, 1, 2, 9, 3, 3])
    arr = np.array([arr1, arr2, arr3, arr4])

    new_arr, new_idx = reorder(arr)
    assert np.array_equal(
        new_arr, [[1, 1, 2, 9, 3, 3], [1, 1, 2, 2, 3, 3], [0, 1, 2, 0, 1, 2]]
    )
    assert np.array_equal(new_idx, [3, 0, 1])
