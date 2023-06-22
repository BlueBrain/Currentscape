"""Script based from https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb
    under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license.
"""
# Preliminaries and Modules
import numpy as np
from scipy.integrate import odeint
from single_compartment import single_compartment
from get_currents import model
import currentscape


def plot_from_original_paper(t0=0.0, tf=10000.0, dt=0.1):
    """Plot currentscape using original paper data.

    Args:
        t0 (float): begin time of simulation (in ms)
        tf (float): end time of simulation (in ms)
        dt (float): time step (in ms)
    """
    # specify the path to initial conditions and paramters files
    config = "config.json"

    pathtocis = (
        "parameters-and-initial-conditions/initial-conditions.txt"
    )
    pathtoparameters = (
        "parameters-and-initial-conditions/model-A-name-HZFTSB.txt"
    )

    # load initialconditions and parameters

    y0 = np.genfromtxt(pathtocis)
    parameters = np.genfromtxt(pathtoparameters)

    # define temperature (set to 10 C)
    temp = 10

    # define integration interval and temporal resolution
    t = np.arange(t0, tf, dt)

    # integration is performed using odeint, a built-in python package to integrate Ordinary Differential Equations
    fullsolution = odeint(
        single_compartment,
        y0,
        t,
        args=(
            parameters,
            temp,
        ),
    )

    # define voltage and currents for currentscape plotting
    voltage = fullsolution[:, 0]
    currents = model(fullsolution, parameters, temp)

    # plot currentscape (full temporal range)
    fig = currentscape.plot(voltage, currents, config)


if __name__ == "__main__":
    plot_from_original_paper()
