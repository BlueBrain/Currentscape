"""Stimuli classes."""
import abc
import logging
import numpy

from bluepyopt.ephys.stimuli import Stimulus

logger = logging.getLogger(__name__)


# taken from BluePyEModel
class BPEMStimulus(Stimulus, metaclass=abc.ABCMeta):

    """BPEM current stimulus"""

    name = ""

    def __init__(
        self,
        step_amplitude,
        step_delay,
        total_duration,
        step_duration,
        holding_current,
        location,
    ):
        """Constructor
        Args:
            location(Location): location of stimulus
        """

        super().__init__()

        self.step_amplitude = step_amplitude
        self.step_delay = step_delay
        self.total_duration = total_duration
        self.step_duration = step_duration
        self.holding_current = holding_current
        self.location = location

        self.iclamp = None
        self.current_vec = None
        self.time_vec = None

    def instantiate(self, sim=None, icell=None):
        """Run stimulus"""

        time_series, current_series = self.generate(dt=0.1)

        icomp = self.location.instantiate(sim=sim, icell=icell)

        self.iclamp = sim.neuron.h.IClamp(icomp.x, sec=icomp.sec)
        self.iclamp.dur = time_series[-1]

        self.current_vec = sim.neuron.h.Vector()
        self.time_vec = sim.neuron.h.Vector()

        for t, i in zip(time_series, current_series):
            self.time_vec.append(t)
            self.current_vec.append(i)

        self.iclamp.delay = 0
        self.current_vec.play(
            self.iclamp._ref_amp,  # pylint:disable=W0212
            self.time_vec,
            1,
            sec=icomp.sec,
        )

    def destroy(self, sim=None):  # pylint:disable=W0613
        """Reset instantiated attributes to None."""

        self.iclamp = None
        self.time_vec = None
        self.current_vec = None

    @abc.abstractmethod
    def generate(self, dt=0.1):  # pylint:disable=W0613
        """Return current time series

        WARNING: do not offset ! This is on-top of a holding stimulus."""
        raise NotImplementedError

    def __str__(self):
        """String representation"""

        return "%s current played at %s" % (self.name, self.location)


# taken from BluePyEModel
class SAHP(BPEMStimulus):

    """sAHP current stimulus"""

    name = "sAHP"

    def __init__(self, location, **kwargs):
        """Constructor
        Args:
            location(Location): location of stimulus
        """

        for k in [
            "delay",
            "totduration",
            "amp",
            "tmid",
            "tmid2",
            "toff",
            "long_amp",
            "holding_current",
        ]:
            if k not in kwargs:
                raise Exception(
                    "Argument {} missing for initialisation of "
                    "eCode {}".format(k, self.name)
                )

        self.tmid = kwargs["tmid"]
        self.tmid2 = kwargs["tmid2"]
        self.toff = kwargs["toff"]
        self.long_amp = kwargs["long_amp"]

        super().__init__(
            step_amplitude=kwargs["amp"],
            step_delay=kwargs["delay"],
            total_duration=kwargs["totduration"],
            step_duration=self.tmid2 - self.tmid,
            holding_current=kwargs["holding_current"],
            location=location,
        )

    def instantiate(self, sim=None, icell=None):
        """Run stimulus"""

        icomp = self.location.instantiate(sim=sim, icell=icell)

        self.iclamp = sim.neuron.h.IClamp(icomp.x, sec=icomp.sec)
        self.iclamp.dur = self.total_duration

        self.current_vec = sim.neuron.h.Vector()
        self.time_vec = sim.neuron.h.Vector()

        self.time_vec.append(0.0)
        self.current_vec.append(self.holding_current)

        self.time_vec.append(self.step_delay)
        self.current_vec.append(self.holding_current)

        self.time_vec.append(self.step_delay)
        self.current_vec.append(self.holding_current + self.long_amp)

        self.time_vec.append(self.tmid)
        self.current_vec.append(self.holding_current + self.long_amp)

        self.time_vec.append(self.tmid)
        self.current_vec.append(self.holding_current + self.step_amplitude)

        self.time_vec.append(self.tmid2)
        self.current_vec.append(self.holding_current + self.step_amplitude)

        self.time_vec.append(self.tmid2)
        self.current_vec.append(self.holding_current + self.long_amp)

        self.time_vec.append(self.toff)
        self.current_vec.append(self.holding_current + self.long_amp)

        self.time_vec.append(self.toff)
        self.current_vec.append(self.holding_current)

        self.time_vec.append(self.total_duration)
        self.current_vec.append(self.holding_current)

        self.iclamp.delay = 0
        self.current_vec.play(
            self.iclamp._ref_amp,  # pylint:disable=W0212
            self.time_vec,
            1,
            sec=icomp.sec,
        )

    def generate(self, dt=0.1):
        """Return current time series

        WARNING: do not offset ! This is on-top of a holding stimulus."""
        t = numpy.arange(0.0, self.total_duration, dt)
        current = numpy.full(t.shape, self.holding_current, dtype="float64")

        ton = int(self.step_delay / dt)
        tmid = int(self.tmid / dt)
        tmid2 = int(self.tmid2 / dt)
        toff = int(self.toff / dt)

        current[ton:tmid] += self.long_amp
        current[tmid2:toff] += self.long_amp
        current[tmid:tmid2] += self.step_amplitude

        return t, current
