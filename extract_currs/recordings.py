"""Recording class."""

import logging
import numpy

import bluepyopt.ephys as ephys

logger = logging.getLogger(__name__)


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

    def instantiate(self, sim=None, icell=None):
        """Instantiate recording."""
        logger.debug(
            "Adding compartment recording of %s at %s", self.variable, self.location
        )

        self.varvector = sim.neuron.h.Vector()
        seg = self.location.instantiate(sim=sim, icell=icell)
        self.varvector.record(getattr(seg, "_ref_%s" % self.variable), 0.1)

        self.segment_area = seg.area()

        self.tvector = sim.neuron.h.Vector()
        self.tvector.record(sim.neuron.h._ref_t, 0.1)  # pylint: disable=W0212

        self.instantiated = True

    @property
    def response(self):
        """Return recording response. Turn current densities into currents."""

        if not self.instantiated:
            return None

        if self.variable == "v":
            return ephys.responses.TimeVoltageResponse(
                self.name, self.tvector.to_python(), self.varvector.to_python()
            )
        else:
            # ionic current: turn mA/cm2 (*um2 / 10.) into pA
            return ephys.responses.TimeVoltageResponse(
                self.name,
                self.tvector.to_python(),
                numpy.array(self.varvector.to_python()) * self.segment_area / 10.0,
            )
