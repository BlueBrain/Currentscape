"""Script taken from https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb
    under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license."""
import numpy as np


def single_compartment(v, t, p, temp):

    V = v[0]
    NaM = v[1]
    NaH = v[2]
    CaTM = v[3]
    CaTH = v[4]
    CaSM = v[5]
    CaSH = v[6]
    HM = v[7]
    KdM = v[8]
    KCaM = v[9]
    AM = v[10]
    AH = v[11]
    IntCa = v[12]
    CaRev = CaNernst(IntCa, temp)

    C = 1.0 * 10  #  // Capacitance (uF / cm^2)

    #    // Ionic Currents (mV / ms)
    #    // double caF = p.get(17);  // Current (nA) to Concentration (uM) Conversion Factor (uM / nA)
    #    // double Ca0 = p.get(18);  // Background Intracellular Calcium Concentration (uM)
    #    // these numbers below convert calcium current to calcium concentration and have not been measured so people change them.

    caF = 0.94
    Ca0 = 0.05
    reftemp = 10

    #     //activation timescale of imi appears to be constant (golowash92)

    tauIntCa = p[35]  # // Calcium buffer time constant (ms)

    #     // Equilibrium Points of Calcium Sensors
    #     // p_g=[gNa, gCaT,gCaS,gA,gKCa,gKd,gH,g_leak]
    #     // Fixed Maximal Conductances

    gNa = p[0]  # // Transient Sodium Maximal Conductance
    gCaT = p[1]  # // Low Threshold Calcium Maximal Conductance
    gCaS = p[2]  # // Slow Calcium Maximal Conductance
    gA = p[3]  # // Transient Potassium Maximal Conductance
    gKCa = p[4]  # // Calcium Dependent Potassium Maximal Conductance
    gKd = p[5]  # // Potassium Maximal Conductance
    gH = p[6]  # // Hyperpolarization Activated Cation Maximal Conductance
    gL = p[7]  # // Leak Maximal Conductance

    EL = p[8]  #   // Leak Reversal Potential
    ENa = p[9]  #  // Sodium Reversal Potential
    ECaT = CaRev  #    // Low Threshold Calcium Reversal Potential
    ECaS = CaRev  #   // Slow Calcium Reversal Potential

    EKd = p[10]  #   // Potassium Reversal Potential
    EKCa = p[10]  #  // Calcium Dependent Potassium Reversal Potential
    EA = p[10]  #    // Transient Potassium Reversal Potential
    EH = p[11]  #    // Hyperpolarization Activated Cation Reversal Potential

    q10_gNa = p[12]
    q10_gNa_m = p[13]
    q10_gNa_h = p[14]

    q10_gCaT = p[15]
    q10_gCaT_m = p[16]
    q10_gCaT_h = p[17]

    q10_gCaS = p[18]
    q10_gCaS_m = p[19]
    q10_gCaS_h = p[20]

    q10_gA = p[21]
    q10_gA_m = p[22]
    q10_gA_h = p[23]

    q10_gKCa = p[24]
    q10_gKCa_m = p[25]

    q10_gKdr = p[27]
    q10_gKdr_m = p[28]

    q10_gH = p[30]
    q10_gH_m = p[31]

    q10_g_leak = p[33]
    q10_tau_Ca = p[34]

    #     Applied Current
    Iapp = p[36]

    #     Steady State Gating Variables
    NaMinf = boltzSS(V, 25.5, -5.29)  # ;  // m^3
    NaHinf = boltzSS(V, 48.9, 5.18)  # ;  // h
    CaTMinf = boltzSS(V, 27.1, -7.20)  # ;  // m^3
    CaTHinf = boltzSS(V, 32.1, 5.50)  # ;  // h
    CaSMinf = boltzSS(V, 33.0, -8.1)  # ;  // m^3
    CaSHinf = boltzSS(V, 60.0, 6.20)  # ;  // h
    HMinf = boltzSS(V, 70.0, 6.0)  # ;  // m
    KdMinf = boltzSS(V, 12.3, -11.8)  # ;  // m^4
    KCaMinf = (IntCa / (IntCa + 3.0)) * boltzSS(V, 28.3, -12.6)  # ;  // m^4
    AMinf = boltzSS(V, 27.2, -8.70)  # ;  // m^3
    AHinf = boltzSS(V, 56.9, 4.90)  # ;  // h

    # // Time Constants (ms)
    tauNaM = tauX(V, 1.32, 1.26, 120.0, -25.0)
    tauNaM = tauNaM * pow(q10_gNa_m, -(temp - reftemp) / 10.0)
    tauNaH = tauX(V, 0.0, -0.67, 62.9, -10.0) * tauX(V, 1.50, -1.00, 34.9, 3.60)
    tauNaH = tauNaH * pow(q10_gNa_h, -(temp - reftemp) / 10.0)
    tauCaTM = tauX(V, 21.7, 21.3, 68.1, -20.5)
    tauCaTM = tauCaTM * pow(q10_gCaT_m, -(temp - reftemp) / 10.0)
    tauCaTH = tauX(V, 105.0, 89.8, 55.0, -16.9)
    tauCaTH = tauCaTH * pow(q10_gCaT_h, -(temp - reftemp) / 10.0)
    tauCaSM = spectau(V, 1.40, 7.00, 27.0, 10.0, 70.0, -13.0)
    tauCaSM = tauCaSM * pow(q10_gCaS_m, -(temp - reftemp) / 10.0)
    tauCaSH = spectau(V, 60.0, 150.0, 55.0, 9.00, 65.0, -16.0)
    tauCaSH = tauCaSH * pow(q10_gCaS_h, -(temp - reftemp) / 10.0)
    tauHM = tauX(V, 272.0, -1499.0, 42.2, -8.73)
    tauHM = tauHM * pow(q10_gH_m, -(temp - reftemp) / 10.0)
    tauKdM = tauX(V, 7.20, 6.40, 28.3, -19.2)
    tauKdM = tauKdM * pow(q10_gKdr_m, -(temp - reftemp) / 10.0)
    tauKCaM = tauX(V, 90.3, 75.1, 46.0, -22.7)
    tauKCaM = tauKCaM * pow(q10_gKCa_m, -(temp - reftemp) / 10.0)
    tauAM = tauX(V, 11.6, 10.4, 32.9, -15.2)
    tauAM = tauAM * pow(q10_gA_m, -(temp - reftemp) / 10.0)
    tauAH = tauX(V, 38.6, 29.2, 38.9, -26.5)
    tauAH = tauAH * pow(q10_gA_h, -(temp - reftemp) / 10.0)

    gNa = gNa * pow(q10_gNa, (temp - reftemp) / 10.0)
    gCaT = gCaT * pow(q10_gCaT, (temp - reftemp) / 10.0)
    gCaS = gCaS * pow(q10_gCaS, (temp - reftemp) / 10.0)
    gA = gA * pow(q10_gA, (temp - reftemp) / 10.0)
    gKCa = gKCa * pow(q10_gKCa, (temp - reftemp) / 10.0)
    gH = gH * pow(q10_gH, (temp - reftemp) / 10.0)
    gKd = gKd * pow(q10_gKdr, (temp - reftemp) / 10.0)
    gL = gL * pow(q10_g_leak, (temp - reftemp) / 10.0)

    tauIntCa = tauIntCa * pow(q10_tau_Ca, -(temp - reftemp) / 10.0)

    iNa = iIonic(gNa, NaM, NaH, 3, V, ENa)
    iCaT = iIonic(gCaT, CaTM, CaTH, 3, V, ECaT)
    iCaS = iIonic(gCaS, CaSM, CaSH, 3, V, ECaS)
    iH = iIonic(gH, HM, 1, 1, V, EH)
    iKd = iIonic(gKd, KdM, 1, 4, V, EKd)
    iKCa = iIonic(gKCa, KCaM, 1, 4, V, EKCa)
    iA = iIonic(gA, AM, AH, 3, V, EA)
    iL = iIonic(gL, 1, 1, 1, V, EL)

    #    // State Equations
    #    // Voltage Time Evolution: C*dV/dt = -I_ionic + I_applied; I_ionic = sum(g_i*m^q*h*(V - E_i))
    # // double dV = (-(iNa + iCaT + iCaS + iH + iKd + iKCa + iA + iL) + iSyns + Iapp)/C;
    # // double intrinsic_currents = iNa + iCaT + iCaS + iH + iKd + iKCa + iA + iL;
    # // cout << intrinsic_currents <<endl;
    dV = (-(iNa + iCaT + iCaS + iH + iKd + iKCa + iA + iL) + Iapp) / C

    # // Gating Variable Time Evolution: dX/dt = (X_inf - X)/tau_X
    dNaM = (NaMinf - NaM) / tauNaM
    dNaH = (NaHinf - NaH) / tauNaH
    dCaTM = (CaTMinf - CaTM) / tauCaTM
    dCaTH = (CaTHinf - CaTH) / tauCaTH
    dCaSM = (CaSMinf - CaSM) / tauCaSM
    dCaSH = (CaSHinf - CaSH) / tauCaSH
    dHM = (HMinf - HM) / tauHM
    dKdM = (KdMinf - KdM) / tauKdM
    dKCaM = (KCaMinf - KCaM) / tauKCaM
    dAM = (AMinf - AM) / tauAM
    dAH = (AHinf - AH) / tauAH

    dIntCa = (-caF * (iCaT + iCaS) - IntCa + Ca0) / tauIntCa
    y_dot = np.zeros(13)
    y_dot[0] = dV
    y_dot[1] = dNaM
    y_dot[2] = dNaH
    y_dot[3] = dCaTM
    y_dot[4] = dCaTH
    y_dot[5] = dCaSM
    y_dot[6] = dCaSH
    y_dot[7] = dHM
    y_dot[8] = dKdM
    y_dot[9] = dKCaM
    y_dot[10] = dAM
    y_dot[11] = dAH
    y_dot[12] = dIntCa
    return y_dot


def boltzSS(Volt, A, B):
    act = 1.0 / (1.0 + np.exp((Volt + A) / B))
    return act


# // Time constants of activation-inactivation
def tauX(Volt, CT, DT, AT, BT):
    timeconst = CT - DT / (1.0 + np.exp((Volt + AT) / BT))
    return timeconst


# // Some currents require a special time constant function
def spectau(Volt, CT, DT, AT, BT, AT2, BT2):
    spec = CT + DT / (np.exp((Volt + AT) / BT) + np.exp((Volt + AT2) / BT2))
    return spec


def iIonic(g, m, h, q, Volt, Erev):
    flux = g * pow(m, q) * h * (Volt - Erev)
    return flux


# // Concentration dependent Ca reversal potential
def CaNernst(CaIn, temp):
    R = 8.314 * pow(10, 3)  # Ideal Gas Constant (*10^3 to put into mV)
    T = 273.15 + temp  # Temperature in Kelvin
    z = 2.0  # Valence of Calcium Ions
    Far = 96485.33  # Faraday's Constant
    CaOut = 3000.0  # Outer Ca Concentration (uM)
    CalRev = ((R * T) / (z * Far)) * np.log10(CaOut / CaIn)
    return CalRev
