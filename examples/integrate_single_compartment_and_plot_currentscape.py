"""Script based from https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb
    under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license.
    Please, run this script from base directory."""
# Preliminaries and Modules
import numpy as np
from scipy.integrate import odeint
from examples.single_compartment import single_compartment
from examples.get_currents import model
from currentscape.currentscape import plot_currentscape


def plot_from_original_paper():
    # specify the path to initial conditions and paramters files
    config = "examples/config.json"

    pathtocis = "examples/parameters-and-initial-conditions/initial-conditions.txt"
    pathtoparameters = (
        "examples/parameters-and-initial-conditions/model-A-name-HZFTSB.txt"
    )
    # pathtoparameters ='./parameters-and-initial-conditions/model-B-name-8XCUQE.txt'
    # pathtoparameters ='./parameters-and-initial-conditions/model-D-name-KI47XV.txt'
    # pathtoparameters ='./parameters-and-initial-conditions/model-D-name-KI47XV.txt'
    # pathtoparameters ='./parameters-and-initial-conditions/model-E-name-OG1RE2.txt'
    # pathtoparameters ='./parameters-and-initial-conditions/model-F-name-B7S21N.txt'

    # load initialconditions and parameters

    y0 = np.genfromtxt(pathtocis)
    parameters = np.genfromtxt(pathtoparameters)

    # define temperature (set to 10 C)
    temp = 10

    # define integration interval and temporal resolution
    t0 = 0.0
    tf = 10000.0  # 10 second duration (10000 msec)
    dt = 0.1
    t = np.arange(t0, tf, dt)

    # integration is performed using odeint, a built-in python package to integrate Ordinary Differential Equations
    fullsolution = odeint(single_compartment, y0, t, args=(parameters, temp,))

    # define voltage and currents for currentscape plotting
    voltage = fullsolution[:, 0]
    currents = model(fullsolution, parameters, temp)

    # plot currentscape (full temporal range)
    fig = plot_currentscape(voltage, currents, config)


if __name__ == "__main__":
    plot_from_original_paper()
