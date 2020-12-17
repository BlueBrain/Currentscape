"""Functions processing data."""

# pylint: disable=too-many-statements
import logging
from math import floor, log10

import numpy as np

logging.basicConfig()  # needed for python2
logger = logging.getLogger(__name__)


def chunksize_warning(cs, len_curr, new_cs):
    """Warns that chunksize has been re-set."""
    logger.warning(
        "x-chunksize (%d) should be a divisor of data size (%d)." % (cs, len_curr)
        + " x-chunksize has been reset to %d." % new_cs
    )


def check_chunksize(cs, len_curr):
    """Set chunksize to a divisor of the data size if not the case.

    Args:
        cs (int): chunksize of data to check
        len_curr (int): data size (length of one current list)
    """
    if cs > len_curr:
        chunksize_warning(cs, len_curr, len_curr)
        return len_curr
    elif cs < 1:
        chunksize_warning(cs, len_curr, 1)
        return 1

    # if chunksize is a divisor: end of loop.
    # else: decrement chunksize by one and retest until a divisor is found.
    i = 0
    len_curr = float(len_curr)
    while len_curr // (cs - i) != len_curr / (cs - i):
        i += 1

    if i != 0:
        chunksize_warning(cs, len_curr, cs - i)
    return cs - i


def sum_chunks(x, chunk_size):
    """Compute the sums of parts of an array.

    Taken from https://stackoverflow.com/questions/18582544/sum-parts-of-numpy-array.
    """
    chunk_size = check_chunksize(int(chunk_size), len(x[0]))

    rows, cols = x.shape
    x = x.reshape(int(x.size / chunk_size), chunk_size)
    return x.sum(axis=1).reshape(rows, int(cols / chunk_size))


def remove_zero_arrays(arr, idx=None):
    """Removes all arrays made only of zeros.

    Returns new array and indexes to previous array indexes.
    """
    if idx is None:
        idx = np.arange(len(arr))

    # do not take nan values into account
    arr_tmp = arr[:, ~np.isnan(arr).any(axis=0)]
    selection = ~np.all(arr_tmp == 0, axis=1)

    return arr[selection], idx[selection]


def reordered_idx(arr):
    """Returns indexes of sorted currents %age from smaller to larger absolute summed values."""
    # do not take nan values into account
    arr = arr[:, ~np.isnan(arr).any(axis=0)]
    return np.argsort(np.sum(np.abs(arr), axis=1))


def reorder(arr):
    """Remove zeros, reorder data and also return data's original indexes."""
    arr, idx = remove_zero_arrays(arr)
    new_i = reordered_idx(arr)[::-1]  # reorder from larger to smaller
    arr = arr[new_i]
    idx = idx[new_i]

    return arr, idx


def autoscale_ticks_and_ylim(c, pos, neg, config_key="current"):
    """Autoscale ticks and ylim and put the result in config.

    No need to return config, since dict are mutable in python.

    Args:
        c (dict): config
        pos (ndarray or float): positive values or max of positive values
        neg (ndarray or float): absolute values of negative values or
            absolute value of minimum of negative values
        config_key (str): key for getting data from config. Should be 'current' or 'ions'
    """
    max_pos = np.max(pos)
    max_neg = np.max(neg)
    maxi = max_pos if max_pos > max_neg else max_neg

    c[config_key]["ylim"] = (5.0 * maxi / 1e7, 5.0 * maxi)

    # order of magnitude. e.g. for 1234 -> 1000, or 0.0456 -> 0.01
    mag_order = pow(10, floor(log10(abs(maxi))))
    # e.g. 0.0456 -> 0.04, 723 -> 700
    sig = float(mag_order * (maxi // mag_order))

    c[config_key]["ticks"] = [sig * 0.00001, sig * 0.001, sig * 0.1]
