"""Run the cell to record currents and ionic concentrations."""

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

import logging
from pathlib import Path

from bluepyopt import ephys
from emodelrunner.load import load_emodel_params
from emodelrunner.load import load_mechanisms
from emodelrunner.load import load_unoptimized_parameters
from emodelrunner.morphology.morphology import SSCXNrnFileMorphology
from emodelrunner.output import write_responses
from emodelrunner.recordings import RecordingCustom

logger = logging.getLogger(__name__)


def absolute_path(path):
    path_to_dir = Path( __file__ ).parent.absolute()
    return str(path_to_dir / path)


def create_cell():
    unopt_params_path = absolute_path("config/params/pyr.json")

    mechs = load_mechanisms(unopt_params_path)

    params = load_unoptimized_parameters(unopt_params_path, v_init=-80, celsius=34)

    morph_path = absolute_path(
        "morphology/dend-C231296A-P4B2_axon-C200897C-P2_-_Scale_x1.000_y0.975_z1.000.asc"
    )
    morph = SSCXNrnFileMorphology(
        morphology_path=morph_path,
        do_replace_axon=True,
        axon_stub_length=60,
        axon_nseg_frequency=15,
    )

    return ephys.models.CellModel(
        name="cADpyr_L4UPC",
        morph=morph,
        mechs=mechs,
        params=params,
    )


def create_recordings(soma_loc):
    recs = []
    currents = [
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

    recs.append(RecordingCustom(name="v", location=soma_loc, variable="v"))

    for var in currents:
        recs.append(RecordingCustom(name=var, location=soma_loc, variable=var))

    for var in ionic_concentrations:
        recs.append(RecordingCustom(name=var, location=soma_loc, variable=var))

    return recs

def create_stimuli(soma_loc):
    # create step stimulus
    stim = ephys.stimuli.NrnSquarePulse(
        step_amplitude=0.34859375,
        step_delay=70.0,
        step_duration=200.0,
        location=soma_loc,
        total_duration=300.0,
    )

    # create holding stimulus
    hold_stim = ephys.stimuli.NrnSquarePulse(
        step_amplitude=-0.0896244038173676,
        step_delay=0.0,
        step_duration=300.0,
        location=soma_loc,
        total_duration=300.0,
    )

    return [stim, hold_stim]


def run():
    cell = create_cell()

    release_params = load_emodel_params(
        params_path=absolute_path("config/params/final.json"), emodel="cADpyr_L4UPC"
    )

    sim = ephys.simulators.NrnSimulator(dt=0.025, cvode_active=False)

    soma_loc = ephys.locations.NrnSeclistCompLocation(
        name="soma", seclist_name="somatic", sec_index=0, comp_x=0.5
    )

    recs = create_recordings(soma_loc)

    stims = create_stimuli(soma_loc)

    protocol = ephys.protocols.SweepProtocol("step_protocol", stims, recs, cvode_active=False)

    logger.info("Python Recordings Running...")
    responses = protocol.run(
        cell_model=cell, param_values=release_params, sim=sim, isolate=False
    )

    write_responses(responses, absolute_path("python_recordings"))

    logger.info("Python Recordings Done")


if __name__ == "__main__":
    run()
