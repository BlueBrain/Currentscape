"""Unit test extract currents functions."""

import numpy as np
from pathlib import Path

from extract_currs.output import write_output


def test_write_output():
    """Test write_output function."""
    output_dir = "tests/output"
    responses = {
        "holding_current": -0.2,
        "StepProtocol_300.soma": {"time": [0, 1, 2], "voltage": [-80, -79, -78]},
    }

    write_output(responses, output_dir)

    new_file = Path(output_dir) / "StepProtocol_300.soma.dat"
    assert not (Path(output_dir) / "holding_current.dat").is_file()
    assert new_file.is_file()

    data = np.loadtxt(new_file)
    time = data[:, 0]
    v = data[:, 1]
    assert np.all(time == np.array([0, 1, 2]))
    assert np.all(v == np.array([-80, -79, -78]))
