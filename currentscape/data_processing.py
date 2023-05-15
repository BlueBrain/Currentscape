"""Functions processing data."""

# Copyright 2023 Blue Brain Project / EPFL

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=too-many-statements
import logging
from math import floor, log10

import numpy as np

logger = logging.getLogger(__name__)


def chunksize_warning(cs, len_curr, new_cs):
    """Warns that chunksize has been re-set.

    Args:
        cs (int): chunksize of data
        len_curr (int): data size (length of one current list)
        new_cs (int): new chunksize to be used
    """
    logger.warning(
        "x-chunksize (%d) should be a divisor of data size (%d)."
        " x-chunksize has been reset to %d.",
        cs,
        len_curr,
        new_cs,
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
    """Compute the sums of parts of an array, then divide values by chunk size.

    Taken from https://stackoverflow.com/questions/18582544/sum-parts-of-numpy-array.

    Args:
        x (ndarray): data to sum into chunks
        chunk_size (int): chunk size of the data to be output
    """
    chunk_size = check_chunksize(int(chunk_size), len(x[0]))

    rows, cols = x.shape
    x = x.reshape(int(x.size / chunk_size), chunk_size)
    x = x.sum(axis=1).reshape(rows, int(cols / chunk_size))
    return x / chunk_size


def remove_zero_arrays(arr, idx=None):
    """Removes all arrays made only of zeros.

    Returns new array and indexes to previous array indexes.

    Args:
        arr (ndarray of ndarrays): array
        idx (ndarray): indices of the array
    """
    if idx is None:
        idx = np.arange(len(arr))

    # do not take nan values into account
    arr_tmp = arr[:, ~np.isnan(arr).any(axis=0)]
    selection = ~np.all(arr_tmp == 0, axis=1)

    return arr[selection], idx[selection]


def reordered_idx(arr):
    """Returns indexes of sorted currents %age from smaller to larger absolute summed values.

    Args:
        arr (ndarray of ndarrays): array
    """
    # do not take nan values into account
    arr = arr[:, ~np.isnan(arr).any(axis=0)]
    return np.argsort(np.sum(np.abs(arr), axis=1))


def reorder(arr):
    """Remove zeros, reorder data and also return data's original indexes.

    Args:
        arr (ndarray of ndarrays): array
    """
    arr, idx = remove_zero_arrays(arr)
    new_i = reordered_idx(arr)[::-1]  # reorder from larger to smaller
    arr = arr[new_i]
    idx = idx[new_i]

    return arr, idx


def order_of_mag(n):
    """Get order of magnitude of a (absolute value of a) number.

    e.g. for 1234 -> 1000, or 0.0456 -> 0.01

    Args:
        n (float or int): number
    """
    return pow(10, floor(log10(abs(n))))


def round_down_sig_digit(n, mag_order=None):
    """Round down to a given number (default: 1) of significant digit.

    e.g. 0.0456 -> 0.04, 723 -> 700

    Args:
        n (float or int): number to be rounded down
        mag_order (float or int): 10 to the power of the desired order of magnitude
            (e.g. 1000 to round the thousands)
            if None: n is rounded to 1 sig digit
    """
    if mag_order is None:
        mag_order = order_of_mag(n)

    # when dealing with floats, floating point errors can happen (e.g. 0.5 // 0.1 -> 0.4)
    # this can happen when n is already its own sig (sig = rounded down one significant digit nmb)
    # (if it's bigger, usually n - sig is bigger than (float(n) - true n value) error
    # so the error does not influence the result of n // mag_order when n != sig(n))
    # -> if (dealing with floats) and (n == sig(n)), then return n
    if mag_order < 1 and len(str(abs(n))) == len(str(mag_order)):
        return n

    return float(mag_order * (n // mag_order))


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

    # e.g. 0.0456 -> 0.04, 723 -> 700
    sig = round_down_sig_digit(maxi)

    c[config_key]["ticks"] = [sig * 0.00001, sig * 0.001, sig * 0.1]
