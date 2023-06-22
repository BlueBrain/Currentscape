"""Plot currentscape."""

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

from pathlib import Path
import numpy as np

import currentscape

from run import absolute_path

def plot():
    data_dir = absolute_path("python_recordings")
    currs = [
        "i_pas",
        "ihcn_Ih",
        "ica_Ca_HVA2",
        "ica_Ca_LVAst",
        "ik_SK_E2",
        "ik_SKv3_1",
        "ik_K_Pst",
        "ik_K_Tst",
        "ina_NaTg",
    ]
    ionic_concentrations = ["cai", "ki", "nai"]

    # load voltage data
    v_path = Path(data_dir) / "v.dat"
    voltage = np.loadtxt(v_path)[:, 1] # load 2nd column. 1st column is time.

    # load currents from files
    currents = []
    for curr in currs:
        file_path = Path(data_dir) / f"{curr}.dat"
        currents.append(np.loadtxt(file_path)[:, 1]) # load 2nd column. 1st column is time.
    currents = np.array(currents)

    # load ionic concentrations from files
    ions = []
    for ion in ionic_concentrations:
        file_path = Path(data_dir) / f"{ion}.dat"
        ions.append(np.loadtxt(file_path)[:, 1]) # load 2nd column. 1st column is time.
    ions = np.array(ions)


    # define config
    # can pass a config file
    # config = absolute_path("path/to/config")
    # can also pass config as a dictionnary
    curr_names = ["pas", "Ih", "Ca_HVA2", "Ca_LVAst", "SK_E2", "SKv3_1", "K_Pst", "K_Tst", "NaTg"]
    config = {
        "current": {"names": curr_names},
        "ions":{"names": ["ca", "k", "na"]},
        "legendtextsize": 5,
    }


    # produce currentscape figure
    fig = currentscape.plot(voltage, currents, config, ions)
    return fig

if __name__ == "__main__":
    fig = plot()
    fig.show()
