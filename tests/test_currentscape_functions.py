"""Test currentscape functions."""

import numpy as np

from currentscape.data_processing import (
    autoscale_ticks_and_ylim,
    sum_chunks,
    check_chunksize,
    reorder,
    order_of_mag,
    round_down_sig_digit,
)
from currentscape.datasets import DataSet


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
    assert np.array_equal(sum_chunks(arr, 2), [[2, 4, 6], [1, 2, 3]])
    assert np.array_equal(sum_chunks(arr, 3), [[4, 8], [3, 3]])


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


def test_dataset_xticks():
    """Test the DataSet function that automatically sets xticks."""
    ds1 = DataSet(data=None, time=np.arange(0, 2000, 10))
    assert np.array_equal(
        ds1.xticks, [0.0, 250.0, 500.0, 750.0, 1000.0, 1250.0, 1500.0, 1750.0]
    )

    ds2 = DataSet(data=None, time=np.arange(0, 2001, 10))
    assert np.array_equal(ds2.xticks, [0, 500, 1000, 1500, 2000])

    ds3 = DataSet(data=None, time=np.array([0, 0.51]))
    # round to avoid floating errors
    ds3ticks = np.around(ds3.xticks, decimals=1)
    expected_ds3 = np.around([0.0, 0.1, 0.2, 0.3, 0.4, 0.5], decimals=1)
    assert np.array_equal(ds3ticks, expected_ds3)

    ds4 = DataSet(data=None, time=np.arange(1002, 1055, 1))
    assert np.array_equal(ds4.xticks, [1010, 1020, 1030, 1040, 1050])

    ds5 = DataSet(data=None, time=np.arange(999, 1005, 1))
    assert np.array_equal(ds5.xticks, [999, 1000, 1001, 1002, 1003, 1004])
