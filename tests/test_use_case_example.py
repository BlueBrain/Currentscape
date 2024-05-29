"""Test that example produces a figure."""

import os
import subprocess
import sys
from tests.utils import cwd

EXAMPLE_FOLDER = os.path.join("examples", "use_case")
sys.path.insert(0, os.path.abspath(EXAMPLE_FOLDER))


def test_extraction_and_plot():
    with cwd(EXAMPLE_FOLDER):
        from run import run
        from plot import plot

        subprocess.call(["nrnivmodl", "mechanisms"])
        run()
        outputs = [
            "cai.dat",
            "i_pas.dat",
            "ica_Ca_HVA2.dat",
            "ica_Ca_LVAst.dat",
            "ihcn_Ih.dat",
            "ik_K_Pst.dat",
            "ik_K_Tst.dat",
            "ik_SK_E2.dat",
            "ik_SKv3_1.dat",
            "ina_NaTg.dat",
            "ki.dat",
            "nai.dat",
            "v.dat",
        ]

    for output in outputs:
        assert os.path.isfile(os.path.join(EXAMPLE_FOLDER, "python_recordings", output))

    fig = plot()
    assert len(fig.axes) == 6
