import numpy as np
from neuron import h
from neuron.units import ms, mV
from currentscape.currentscape import plot_currentscape


def main():
    current_names = ["Potassium", "Sodium", "Leak"]

    voltage, potassium, sodium, leak = run_sim()

    config = {
        "output": {
            "savefig": True,
            "dir": ".",
            "fname": "quickstart_plot",
            "extension": "png",
            "dpi": 300,
            "transparent": False
        },
        "current": {"names": current_names},
        "voltage": {"ylim": [-90, 50]},
        "legendtextsize": 5,
        "adjust": {
            "left": 0.15,
            "right": 0.8,
            "top": 1.0,
            "bottom": 0.0
        }
    }

    fig = plot_currentscape(voltage, [potassium, sodium, leak], config)
    fig.show()


def run_sim():
    h.load_file('stdrun.hoc')

    soma = h.Section(name='soma')
    dend = h.Section(name='dend')

    dend.connect(soma(1))

    soma.L = soma.diam = 12.6157
    dend.L = 200
    dend.diam = 1

    for sec in h.allsec():
        sec.Ra = 100    # Axial resistance in Ohm * cm
        sec.cm = 1      # Membrane capacitance in micro Farads / cm^2

    # Insert active Hodgkin-Huxley current in the soma
    soma.insert('hh')
    for seg in soma:
        seg.hh.gnabar = 0.12  # Sodium conductance in S/cm2
        seg.hh.gkbar = 0.036  # Potassium conductance in S/cm2
        seg.hh.gl = 0.0003    # Leak conductance in S/cm2
        seg.hh.el = -54.3     # Reversal potential in mV

    # Insert passive current in the dendrite
    dend.insert('pas')
    for seg in dend:
        seg.pas.g = 0.001  # Passive conductance in S/cm2
        seg.pas.e = -65    # Leak reversal potential mV

    stim = h.IClamp(dend(1))
    stim.delay = 5
    stim.dur = 10
    stim.amp = 0.1

    t_vec = h.Vector()
    v_vec = h.Vector()
    ik_vec = h.Vector()
    ina_vec = h.Vector()
    il_vec = h.Vector()
    t_vec.record(h._ref_t)
    v_vec.record(soma(0.5)._ref_v)
    ik_vec.record(soma(0.5)._ref_ik)
    ina_vec.record(soma(0.5)._ref_ina)
    il_vec.record(soma(0.5)._ref_il_hh)

    h.finitialize(-65 * mV)
    h.continuerun(25 * ms)

    to_pA = 10 * soma(0.5).area()  # turn mA/cm2 (*um2) into pA
    voltage = np.asarray(v_vec)
    potassium = np.asarray(ik_vec) * to_pA
    sodium = np.asarray(ina_vec) * to_pA
    leak = np.asarray(il_vec) * to_pA

    return voltage, potassium, sodium, leak


if __name__ == "__main__":
    main()
