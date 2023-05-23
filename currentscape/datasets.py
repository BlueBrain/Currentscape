"""Base class Dataset."""

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

import numpy as np

from currentscape.data_processing import round_down_sig_digit, order_of_mag


class DataSet:
    """Base class containing data and data-handling methods."""

    def __init__(self, data, names=None, time=None, xticks=None):
        """Constructor.

        Args:
            data (list of lists): data
                all lists are expected to have the same size.
            names (list of str): names corresponding to the data,
                in the same order
            time (list): time of the data
            xticks (list): ticks on the x axis. Determined automatically if None.

        Attributes:
            data (ndarray of ndarray): data
            names (ndarray of str): names corresponding to the data,
                in the same order
            time (ndarray): time of the data
            N (int): size of data
            x_size (int): size of one element of data
            idxs (ndarray of ints): arr containing indexes after a reordering
                s.t. reordered_data = self.data[self.idxs]
            xticks (ndarray): ticks on the x axis. Determined automatically if None.
        """
        self.data = None
        self.N = None
        self.x_size = None
        self.idxs = None

        self.names = None

        self.time = None
        self.xticks = None

        if data is not None:
            self.data = np.asarray(data)

            self.N = len(self.data)
            self.idxs = range(self.N)

            if self.N > 0:
                self.x_size = len(self.data[0])
            else:
                self.x_size = 0

        if names is not None:
            self.names = np.asarray(names)

        if time is not None:
            self.time = np.asarray(time)
        elif self.x_size:
            self.time = np.arange(self.x_size)

        if xticks is not None:
            self.xticks = np.asarray(xticks)
        elif self.time is not None:
            self.xticks = self.set_xticks()

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

    def set_xticks(self):
        """Generate x ticks values depending on time."""
        if self.time is None or len(self.time) == 0:
            return None
        # a diff == 0 would make this function crash.
        # Returning the only xticks making any sense in that case.
        elif len(self.time) == 1:
            return self.time.copy()

        tmin = self.time[0]
        tmax = self.time[-1]
        diff = tmax - tmin

        # order of magnitude
        mag_order = order_of_mag(diff)
        sig = round_down_sig_digit(diff, mag_order)

        if sig / mag_order >= 5:
            step = mag_order
        elif sig / mag_order >= 2:
            step = mag_order / 2.0
        else:
            step = mag_order / 4.0

        if tmin == 0:
            start = 0
        # xticks can begin before tmin. this is corrected afterwards
        else:
            start = round_down_sig_digit(tmin, mag_order)

        # if last step end up on tmax when the list to be returned is created
        # make 'stop' higher than tmax to include tmax in returned value.
        if (tmax - start) % step == 0:
            stop = tmax + step / 2.0
        else:
            stop = tmax

        xticks = np.arange(start, stop, step)

        # remove values lower than the 1st time.
        xticks = [x for x in xticks if x >= tmin]

        return np.array(xticks)

    def xticks_for_imshow(self):
        """Return xticks when the xaxis goes from 0 to x_size."""
        if self.xticks is None or self.time is None or self.x_size is None:
            return None
        elif len(self.time) == 1:
            return self.time

        tmin = self.time[0]
        tmax = self.time[-1]
        diff = tmax - tmin

        return (self.xticks - tmin) / diff * self.x_size
