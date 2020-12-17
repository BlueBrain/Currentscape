"""Mappers."""

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
        for i in range(currents):
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
