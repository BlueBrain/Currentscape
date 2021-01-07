"""Recording class."""

import logging
import numpy

import bluepyopt.ephys as ephys

logger = logging.getLogger(__name__)


def get_loc_ion_list(isection):
    """Get all ion concentrations available in a location."""
    local_ion_list = []

    # ion concentration
    ions = isection.psection()["ions"]
    for _, ion in ions.items():
        for concentration in ion.keys():
            # concentration should have 'i' at the end (e.g. ki, cai, nai, ...)
            if concentration[-1] == "i":
                local_ion_list.append(concentration)

    return local_ion_list


def get_loc_varlist(isection):
    """Get all possible variables in a location."""
    local_varlist = []

    # currents etc.
    raw_dict = isection.psection()["density_mechs"]
    for channel, vars_ in raw_dict.items():
        for var in vars_.keys():
            local_varlist.append("_".join((var, channel)))

    local_varlist.append("v")

    return local_varlist


def check_recordings(recordings, icell, sim):
    """Returns a list of valid recordings (where the variable is in the location)."""

    new_recs = []  # to return
    varlists = {}  # keep varlists to avoid re-computing them every time

    for rec in recordings:
        # get section from location
        seg = rec.location.instantiate(sim=sim, icell=icell)
        sec = seg.sec
        section_key = str(sec)

        # get list of variables available in the section
        if section_key in varlists:
            local_varlist = varlists[section_key]
        else:
            local_varlist = get_loc_varlist(sec) + get_loc_ion_list(sec)
            varlists[section_key] = local_varlist

        # keep recording if its variable is available in its location
        if rec.variable in local_varlist:
            new_recs.append(rec)

    return new_recs


class RecordingCustom(ephys.recordings.CompRecording):
    """Response to stimulus with recording every 0.1 ms.

    Also records current densities as well as the segment area to get currents.
    """

    def __init__(self, name=None, location=None, variable="v"):
        """Constructor.

        Args:
            name (str): name of this object
            location (Location): location in the model of the recording
            variable (str): which variable to record from (e.g. 'v')
        """
        super(RecordingCustom, self).__init__(
            name=name, location=location, variable=variable
        )

        # important to turn current densities into currents
        self.segment_area = None
        # important to detect ion concentration variable
        self.local_ion_list = None

    def instantiate(self, sim=None, icell=None):
        """Instantiate recording."""
        logger.debug(
            "Adding compartment recording of %s at %s", self.variable, self.location
        )

        self.varvector = sim.neuron.h.Vector()
        seg = self.location.instantiate(sim=sim, icell=icell)
        self.varvector.record(getattr(seg, "_ref_%s" % self.variable), 0.1)

        self.segment_area = seg.area()
        self.local_ion_list = get_loc_ion_list(seg.sec)

        self.tvector = sim.neuron.h.Vector()
        self.tvector.record(sim.neuron.h._ref_t, 0.1)  # pylint: disable=W0212

        self.instantiated = True

    @property
    def response(self):
        """Return recording response. Turn current densities into currents."""

        if not self.instantiated:
            return None

        # do not modify voltage or ion concentration
        if self.variable == "v" or self.variable in self.local_ion_list:
            return ephys.responses.TimeVoltageResponse(
                self.name, self.tvector.to_python(), self.varvector.to_python()
            )
        else:
            # ionic current: turn mA/cm2 (*um2) into pA
            return ephys.responses.TimeVoltageResponse(
                self.name,
                self.tvector.to_python(),
                numpy.array(self.varvector.to_python()) * self.segment_area * 10.0,
            )
