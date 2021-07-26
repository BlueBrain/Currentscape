"""Test that example produces a figure."""
import os
from examples.integrate_single_compartment_and_plot_currentscape import (
    plot_from_original_paper,
)


def test_example_original_paper():
    _ = plot_from_original_paper(tf=2500.0, dt=1.0)
    assert os.path.isfile(os.path.join("examples", "output", "example.png"))
