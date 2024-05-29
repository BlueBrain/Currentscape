"""Test that example produces a figure."""

import os
import sys
from tests.utils import cwd

EXAMPLE_FOLDER = os.path.join("examples", "original_paper_plot")
sys.path.insert(0, os.path.abspath(EXAMPLE_FOLDER))


def test_example_original_paper():
    with cwd(EXAMPLE_FOLDER):
        from integrate_single_compartment_and_plot_currentscape import (
            plot_from_original_paper,
        )

        _ = plot_from_original_paper(tf=2500.0, dt=1.0)

    assert os.path.isfile(os.path.join(EXAMPLE_FOLDER, "output", "example.png"))
