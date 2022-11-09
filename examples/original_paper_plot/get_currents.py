"""Script taken from https://datadryad.org/stash/dataset/doi:10.5061/dryad.d0779mb
    under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication license."""

from numpy import *
import numpy as np


# Time constant functions
def tauX(Volt, CT, DT, AT, BT):
    timeconst = CT - DT / (1.0 + np.exp((Volt + AT) / BT))
    return timeconst


# Special time constant function (spectau)
def spectau(Volt, CT, DT, AT, BT, AT2, BT2):
    spec = CT + DT / (np.exp((Volt + AT) / BT) + np.exp((Volt + AT2) / BT2))
    return spec


# Ionic currents
# q is the exponent of the activation variable m
def iIonic(g, m, h, q, Volt, Erev):
    flux = g * pow(m, q) * h * (Volt - Erev)
    return flux


# Concentration dependent Ca reversal potential
def CaNernst(CaIn, temp):
    R = 8.314 * pow(10, 3)  # Ideal Gas Constant (*10^3 to put into mV)
    T = 273.15 + temp  # Temperature in Kelvin
    z = 2.0  # Valence of Caclium Ions
    Far = 96485.33  # Faraday's Constant
    CaOut = 3000.0  # Outer Ca Concentration (uM)
    CalRev = ((R * T) / (z * Far)) * np.log(CaOut / CaIn)
    # print 'calrev ', CalRev
    return CalRev


def model(v, p, temp):
    reftemp = 10
    V = v[:, 0]
    NaM = v[:, 1]
    NaH = v[:, 2]
    CaTM = v[:, 3]
    CaTH = v[:, 4]
    CaSM = v[:, 5]
    CaSH = v[:, 6]
    HM = v[:, 7]
    KdM = v[:, 8]
    KCaM = v[:, 9]
    AM = v[:, 10]
    AH = v[:, 11]
    IntCa = v[:, 12]

    CaRev = CaNernst(IntCa, temp)
    tauIntCa = p[35]  # Calcium buffer time constant (ms)
    # Maximal Conductances
    gNa = p[0]  # Transient Sodium Maximal Conductance
    gCaT = p[1]  # Low Threshold Calcium Maximal Conductance
    gCaS = p[2]  # Slow Calcium Maximal Conductance
    gA = p[3]  # Transient Potassium Maximal Conductance
    gKCa = p[4]  # Calcium Dependent Potassium Maximal Conductance
    gKd = p[5]  # Potassium Maximal Conductance
    gH = p[6]  # Hyperpolarization Activated Cation Maximal Conductance
    gL = p[7]  # Leak Maximal Conductance

    # p_Erev = [e_leak,e_na,e_k,e_h]
    EL = p[8]  # Leak Reversal Potential
    ENa = p[9]  # Sodium Reversal Potential
    ECaT = CaRev  # Low Threshold Calcium Reversal Potential
    ECaS = CaRev  # Slow Calcium Reversal Potential

    EKd = p[10]  # Potassium Reversal Potential
    EKCa = p[10]  # Calcium Dependent Potassium Reversal Potential
    EA = p[10]  # Transient Potassium Reversal Potential

    EH = p[11]  # Hyperpolarization Activated Cation Reversal Potential

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

    # Time Constants (ms)
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
    gKd = gKd * pow(q10_gKdr, (temp - reftemp) / 10.0)
    gH = gH * pow(q10_gH, (temp - reftemp) / 10.0)
    gL = gL * pow(q10_g_leak, (temp - reftemp) / 10.0)

    tauIntCa = tauIntCa * pow(q10_tau_Ca, -(temp - reftemp) / 10.0)

    # Ionic Currents (mV / ms)

    iNa = iIonic(gNa, NaM, NaH, 3, V, ENa)
    iCaT = iIonic(gCaT, CaTM, CaTH, 3, V, ECaT)
    iCaS = iIonic(gCaS, CaSM, CaSH, 3, V, ECaS)
    iH = iIonic(gH, HM, 1, 1, V, EH)
    iKd = iIonic(gKd, KdM, 1, 4, V, EKd)
    iKCa = iIonic(gKCa, KCaM, 1, 4, V, EKCa)
    iA = iIonic(gA, AM, AH, 3, V, EA)
    iL = iIonic(gL, 1, 1, 1, V, EL)

    r = [iNa, iCaT, iCaS, iA, iKCa, iKd, iH, iL]
    return r
