"""Base class Dataset."""

import numpy as np


class DataSet:
    """Base class containing data and data-handling methods."""

    def __init__(self, data, names=None):
        """Constructor.

        Args:
            data (list of lists): data
                all lists are expected to have the same size.
            names (list of str): names corresponding to the data,
                in the same order

        Attributes:
            data (ndarray of ndarray): data
            names (ndarray of str): names corresponding to the data,
                in the same order
            N (int): size of data
            x_size (int): size of one element of data
            idxs (ndarray of ints): arr containing indexes after a reordering
                s.t. reordered_data = self.data[self.idxs]
        """
        if data is not None:
            self.data = np.array(data)
            self.names = np.array(names)

            self.N = len(self.data)
            self.idxs = range(self.N)

            if self.N > 0:
                self.x_size = len(self.data[0])
            else:
                self.x_size = 0
        else:
            self.data = None
            self.names = None

            self.N = None
            self.x_size = None
            self.idxs = None

    def get_negative_data(self):
        """Returns a copy of data keeping only negative ones."""
        selected_currs = self.data.copy()
        selected_currs[self.data > 0] = 0

        return selected_currs

    def get_positive_data(self):
        """Returns a copy of data keeping only positive ones."""
        selected_currs = self.data.copy()
        selected_currs[self.data < 0] = 0

        return selected_currs
