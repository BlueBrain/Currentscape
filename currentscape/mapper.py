"""Mappers."""

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

# pylint: disable=deprecated-method
try:
    # python 3
    from math import gcd
except ImportError:
    # python 2
    from fractions import gcd


def has_common_divisor(n1, n2, n):
    """Return True if n has a common divisor with either n1 or n2."""
    if gcd(n, n1) == 1 and gcd(n, n2) == 1:
        return False
    return True


def create_mapper(n_colors, n_patterns):
    """Find a number n that will be useful to find pairs (color, pattern).

    Those pairs should not have the same color in a row and the same pattern in a row.
    n should work as in the following example.

    Example:
        for i in range(n_currents):
            color = (n*i) % n_colors
            pattern = ( (n*i) // n_colors) % n_patterns

    Constraints:
        * For two patterns to be different in a row: n>=n_patterns
        * n should not have a common divisor with either n_colors or n_patterns.
    """
    mapper = n_patterns
    while has_common_divisor(n_colors, n_patterns, mapper):
        mapper += 1
    return mapper


def map_colors(curr_idxs, n_colors, mapper):
    """Get color index(es) s.t. a color / pattern index pair cannot be produced twice.

    Args:
        curr_idxs (int or ndarray of ints): index(es) of the current(s).
            should be smaller than number of currents
        n_colors (int): total number of colors
        mapper (int): number used to mix colors and patterns
    """
    return (mapper * curr_idxs) % n_colors


def map_patterns(curr_idxs, n_colors, n_patterns, mapper):
    """Get pattern index(es) s.t. a color / pattern index pair cannot be produced twice.

    Args:
        curr_idxs (int or ndarray of ints): index(es) of the current(s).
            should be smaller than number of currents
        n_colors (int): total number of colors
        n_patterns (int): total number of patterns
        mapper (int): number used to mix colors and patterns
    """
    return ((mapper * curr_idxs) // n_colors) % n_patterns
