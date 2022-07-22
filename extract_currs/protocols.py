"""Protocols."""

import collections
import copy
import logging
import numpy

from bluepyopt import ephys

from extract_currs.recordings import check_recordings

logger = logging.getLogger(__name__)


class RatSSCxMainProtocol(ephys.protocols.Protocol):
    """Main protocol to fit RatSSCx neuron ephys parameters.

    Pseudo code:
        Find resting membrane potential
        Find input resistance
        If both of these scores are within bounds, run other protocols:
            Find holding current
            Find rheobase
            Run IDRest
            Possibly run other protocols (based on constructor arguments)
            Return all the responses
        Otherwise return return Rin and RMP protocol responses
    """

    def __init__(
        self,
        name,
        rmp_protocol=None,
        rmp_efeature=None,
        rinhold_protocol=None,
        rin_efeature=None,
        thdetect_protocol=None,
        other_protocols=None,
        pre_protocols=None,
        preprot_score_threshold=None,
    ):
        """Constructor."""
        # pylint: disable=too-many-arguments
        super().__init__(name=name)

        self.rmp_protocol = rmp_protocol
        self.rmp_efeature = rmp_efeature

        self.rinhold_protocol = rinhold_protocol
        self.rin_efeature = rin_efeature

        self.thdetect_protocol = thdetect_protocol
        self.other_protocols = other_protocols

        self.pre_protocols = pre_protocols
        self.preprot_score_threshold = preprot_score_threshold

    def subprotocols(self):
        """Return all the subprotocols contained in this protocol, is recursive."""
        subprotocols = collections.OrderedDict({self.name: self})
        subprotocols.update(self.rmp_protocol.subprotocols())
        subprotocols.update(self.rinhold_protocol.subprotocols())
        subprotocols.update(self.thdetect_protocol.subprotocols())
        for other_protocol in self.other_protocols:
            subprotocols.update(other_protocol.subprotocols())
        for pre_protocol in self.pre_protocols:
            subprotocols.update(pre_protocol.subprotocols())

        return subprotocols

    @property
    def rin_efeature(self):
        """Get in_efeature."""
        return self.rinhold_protocol.rin_efeature

    @rin_efeature.setter
    def rin_efeature(self, value):
        """Set rin_efeature."""
        self.rinhold_protocol.rin_efeature = value

    def run(self, cell_model, param_values, sim=None, isolate=None):
        """Run protocol."""
        # pylint: disable=unused-argument
        responses = collections.OrderedDict()

        cell_model.freeze(param_values)

        # Find resting membrane potential
        rmp_response = self.rmp_protocol.run(cell_model, {}, sim=sim)
        responses.update(rmp_response)
        rmp = self.rmp_efeature.calculate_feature(rmp_response)

        # Find Rin and holding current
        rinhold_response = self.rinhold_protocol.run(cell_model, {}, sim=sim, rmp=rmp)

        holding_current = cell_model.holding_current

        if rinhold_response is not None:
            rin = self.rin_efeature.calculate_feature(rinhold_response)

            responses.update(rinhold_response)

            responses.update(
                self.thdetect_protocol.run(
                    cell_model, {}, sim=sim, holdi=holding_current, rmp=rmp, rin=rin
                )
            )

            if cell_model.threshold_current is not None:
                self._run_pre_protocols(cell_model, sim, responses)
                self._run_other_protocols(cell_model, sim, responses)

        cell_model.unfreeze(param_values.keys())

        return responses

    def _run_pre_protocols(self, cell_model, sim, responses):
        """Runs the pre_protocols and updates responses dict."""
        for pre_protocol in self.pre_protocols:
            response = pre_protocol.run(cell_model, {}, sim=sim)
            responses.update(response)

    def _run_other_protocols(self, cell_model, sim, responses):
        """Runs the other_protocols and updates responses dict."""
        for other_protocol in self.other_protocols:
            response = other_protocol.run(cell_model, {}, sim=sim)
            responses.update(response)


class RatSSCxRinHoldcurrentProtocol(ephys.protocols.Protocol):
    """IDRest protocol to fit RatSSCx neuron ephys parameters."""

    def __init__(
        self,
        name,
        rin_protocol_template=None,
        voltagebase_efeature=None,
        voltagebase_score_threshold=None,
        holdi_estimate_multiplier=2,
        holdi_precision=0.1,
        holdi_max_depth=5,
        prefix=None,
    ):
        """Constructor."""
        # pylint: disable=too-many-arguments
        super().__init__(name=name)
        self.rin_protocol_template = rin_protocol_template
        self.voltagebase_efeature = voltagebase_efeature
        self.voltagebase_score_threshold = voltagebase_score_threshold
        self.holdi_estimate_multiplier = holdi_estimate_multiplier
        self.holdi_precision = holdi_precision
        self.holdi_max_depth = holdi_max_depth

        if prefix is None:
            self.prefix = ""
        else:
            self.prefix = prefix + "."

        # This will be set after the run()
        self.rin_protocol = None

        # Set in RatSSCxMainProtocol's setter
        self.rin_efeature = None

    def run(self, cell_model, param_values, sim, rmp=None):
        """Run protocol."""
        responses = collections.OrderedDict()

        # Calculate Rin without holding current
        rin_noholding_protocol = self.create_rin_protocol(holdi=0)
        rin_noholding_response = rin_noholding_protocol.run(
            cell_model, param_values, sim=sim
        )
        rin_noholding = self.rin_efeature.calculate_feature(rin_noholding_response)

        # Search holding current
        holdi = self.search_holdi(
            cell_model,
            param_values,
            sim,
            self.voltagebase_efeature.exp_mean,
            rin_noholding,
            rmp,
        )

        if holdi is None:
            return None

        # Set up Rin protocol
        self.rin_protocol = self.create_rin_protocol(holdi=holdi)

        # Return response
        responses = self.rin_protocol.run(cell_model, param_values, sim)

        responses[self.prefix + "bpo_holding_current"] = holdi

        cell_model.holding_current = holdi

        return responses

    def subprotocols(self):
        """Return subprotocols."""
        subprotocols = collections.OrderedDict({self.name: self})

        subprotocols.update(
            {self.rin_protocol_template.name: self.rin_protocol_template}
        )

        return subprotocols

    def create_rin_protocol(self, holdi=None):
        """Create threshold protocol."""
        rin_protocol = copy.deepcopy(self.rin_protocol_template)
        rin_protocol.name = "Rin"
        for recording in rin_protocol.recordings:
            recording.name = recording.name.replace(
                self.rin_protocol_template.name, rin_protocol.name
            )

        rin_protocol.holding_stimulus.step_amplitude = holdi

        return rin_protocol

    def search_holdi(
        self, cell_model, param_values, sim, holding_voltage, rin_noholding, rmp
    ):
        """Find the holding current to hold cell at holding_voltage."""
        holdi_estimate = float(holding_voltage - rmp) / rin_noholding

        holdi = self.binsearch_holdi(
            holding_voltage,
            cell_model,
            param_values,
            sim,
            upper_bound=0.0,
            lower_bound=self.holdi_estimate_multiplier * holdi_estimate,
            precision=self.holdi_precision,
            max_depth=self.holdi_max_depth,
        )

        return holdi

    def binsearch_holdi(
        self,
        holding_voltage,
        cell_model,
        param_values,
        sim=None,
        lower_bound=None,
        upper_bound=None,
        precision=None,
        max_depth=None,
        depth=1,
    ):
        """Do binary search to find holding current."""
        # pylint: disable=too-many-arguments
        middle_bound = upper_bound - abs(upper_bound - lower_bound) / 2

        if depth > max_depth:
            return middle_bound
        else:
            middle_voltage = self.voltage_base(
                middle_bound, cell_model, param_values, sim=sim
            )
            if abs(middle_voltage - holding_voltage) < precision:
                return middle_bound
            elif middle_voltage > holding_voltage:
                return self.binsearch_holdi(
                    holding_voltage,
                    cell_model,
                    param_values,
                    sim=sim,
                    lower_bound=lower_bound,
                    upper_bound=middle_bound,
                    precision=precision,
                    max_depth=max_depth,
                    depth=depth + 1,
                )
            elif middle_voltage < holding_voltage:
                return self.binsearch_holdi(
                    holding_voltage,
                    cell_model,
                    param_values,
                    sim=sim,
                    lower_bound=middle_bound,
                    upper_bound=upper_bound,
                    precision=precision,
                    max_depth=max_depth,
                    depth=depth + 1,
                )
            else:
                return None

    def voltage_base(self, current, cell_model, param_values, sim=None):
        """Calculate voltage base for certain stimulus current."""
        protocol = self.create_rin_protocol(holdi=current)

        response = protocol.run(cell_model, param_values, sim=sim)

        feature = ephys.efeatures.eFELFeature(
            name="Holding.voltage_base",
            efel_feature_name="voltage_base",
            recording_names={"": self.prefix + "Rin.soma.v"},
            stim_start=protocol.stim_start,
            stim_end=protocol.stim_end,
            exp_mean=0,
            exp_std=0.1,
        )

        voltage_base = feature.calculate_feature(response)

        return voltage_base


class RatSSCxThresholdDetectionProtocol(ephys.protocols.Protocol):
    """IDRest protocol to fit RatSSCx neuron ephys parameters."""

    def __init__(
        self,
        name,
        step_protocol_template=None,
        max_threshold_voltage=-40,
        holding_voltage=None,
        prefix=None,
    ):
        """Constructor."""
        super().__init__(name=name)

        self.step_protocol_template = step_protocol_template
        self.max_threshold_voltage = max_threshold_voltage

        self.short_perc = 0.1
        self.short_steps = 20
        self.holding_voltage = holding_voltage

        if prefix is None:
            self.prefix = ""
        else:
            self.prefix = prefix + "."

    def subprotocols(self):
        """Return subprotocols."""
        subprotocols = collections.OrderedDict({self.name: self})

        subprotocols.update(self.step_protocol_template.subprotocols())

        return subprotocols

    def run(self, cell_model, param_values, sim, holdi, rin, rmp):
        """Run protocol."""
        # pylint: disable=unused-argument
        responses = collections.OrderedDict()

        # Calculate max threshold current
        max_threshold_current = self.search_max_threshold_current(rin=rin, rmp=rmp)

        # Calculate spike threshold
        threshold_current = self.search_spike_threshold(
            cell_model,
            {},
            holdi=holdi,
            lower_bound=-holdi,
            upper_bound=max_threshold_current,
            sim=sim,
        )

        cell_model.threshold_current = threshold_current

        responses[self.prefix + "bpo_threshold_current"] = threshold_current

        return responses

    def search_max_threshold_current(self, rin=None, rmp=None):
        """Find the current necessary to get to max_threshold_voltage."""
        # pylint: disable=unused-argument
        max_threshold_current = (
            float(self.max_threshold_voltage - self.holding_voltage) / rin
        )

        return max_threshold_current

    def create_step_protocol(self, holdi=0.0, step_current=0.0):
        """Create threshold protocol."""
        threshold_protocol = copy.deepcopy(self.step_protocol_template)
        threshold_protocol.name = "Threshold"
        for recording in threshold_protocol.recordings:
            recording.name = recording.name.replace(
                self.step_protocol_template.name, threshold_protocol.name
            )

        if threshold_protocol.holding_stimulus is not None:
            threshold_protocol.holding_stimulus.step_amplitude = holdi

        for step_stim in threshold_protocol.step_stimuli:
            step_stim.step_amplitude = step_current

        return threshold_protocol

    def create_short_threshold_protocol(self, holdi=None, step_current=None):
        """Create short threshold protocol."""
        short_protocol = self.create_step_protocol(
            holdi=holdi, step_current=step_current
        )
        origin_step_duration = short_protocol.stim_duration
        origin_step_delay = short_protocol.stim_start

        short_step_duration = origin_step_duration * self.short_perc
        short_total_duration = origin_step_delay + short_step_duration

        short_protocol.step_stimuli[0].step_duration = short_step_duration
        short_protocol.step_stimuli[0].total_duration = short_total_duration

        if short_protocol.holding_stimulus is not None:
            short_protocol.holding_stimulus.step_duration = short_total_duration
            short_protocol.holding_stimulus.total_duration = short_total_duration

        return short_protocol

    def detect_spike(
        self,
        cell_model,
        param_values,
        sim=None,
        step_current=None,
        holdi=None,
        short=False,
    ):
        """Detect if spike is present at current level."""
        # Only run short pulse if percentage set smaller than 100%
        if short and self.short_perc < 1.0:
            protocol = self.create_short_threshold_protocol(
                holdi=holdi, step_current=step_current
            )
        else:
            protocol = self.create_step_protocol(holdi=holdi, step_current=step_current)

        response = protocol.run(cell_model, param_values, sim=sim)

        feature = ephys.efeatures.eFELFeature(
            name="ThresholdDetection.Spikecount",
            efel_feature_name="Spikecount",
            recording_names={"": self.prefix + "ThresholdDetection.soma.v"},
            stim_start=protocol.stim_start,
            stim_end=protocol.stim_end,
            exp_mean=1,
            exp_std=0.1,
        )

        spike_count = feature.calculate_feature(response)

        return spike_count >= 1

    def binsearch_spike_threshold(
        self,
        cell_model,
        param_values,
        sim=None,
        holdi=None,
        lower_bound=None,
        upper_bound=None,
        precision=0.01,
        max_depth=5,
        depth=1,
    ):
        """Do binary search to find spike threshold.

        Assumption is that lower_bound has no spike, upper_bound has.
        """
        # pylint: disable=too-many-arguments
        if depth > max_depth or abs(upper_bound - lower_bound) < precision:
            return upper_bound
        else:
            middle_bound = upper_bound - abs(upper_bound - lower_bound) / 2
            spike_detected = self.detect_spike(
                cell_model,
                param_values,
                sim=sim,
                holdi=holdi,
                step_current=middle_bound,
                short=False,
            )
            if spike_detected:
                return self.binsearch_spike_threshold(
                    cell_model,
                    param_values,
                    sim=sim,
                    holdi=holdi,
                    lower_bound=lower_bound,
                    upper_bound=middle_bound,
                    depth=depth + 1,
                )
            else:
                return self.binsearch_spike_threshold(
                    cell_model,
                    param_values,
                    sim=sim,
                    holdi=holdi,
                    lower_bound=middle_bound,
                    upper_bound=upper_bound,
                    depth=depth + 1,
                )

    def search_spike_threshold(
        self,
        cell_model,
        param_values,
        sim=None,
        holdi=None,
        lower_bound=None,
        upper_bound=None,
    ):
        """Find the current step spiking threshold."""
        # pylint: disable=undefined-loop-variable
        step_currents = numpy.linspace(lower_bound, upper_bound, num=self.short_steps)

        if len(step_currents) == 0:
            return None

        for step_current in step_currents:
            spike_detected = self.detect_spike(
                cell_model,
                param_values,
                sim=sim,
                holdi=holdi,
                step_current=step_current,
                short=True,
            )

            if spike_detected:
                upper_bound = step_current
                break

        # if upper bound didn't have spike with short stimulus
        # check if there is one with longer stimulus
        if not spike_detected:
            spike_detected = self.detect_spike(
                cell_model,
                param_values,
                sim=sim,
                holdi=holdi,
                step_current=step_current,
                short=False,
            )

            if spike_detected:
                upper_bound = step_current
            else:
                return None

        threshold_current = self.binsearch_spike_threshold(
            cell_model,
            {},
            sim=sim,
            holdi=holdi,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )

        return threshold_current


class SweepProtocolCustom(ephys.protocols.SweepProtocol):
    """Sweep protocol but checking recordings when instantiating."""

    def instantiate(self, sim=None, icell=None):
        """Check recordings, then instantiate."""
        self.recordings = check_recordings(self.recordings, icell, sim)

        super().instantiate(sim, icell)


class StepProtocol(ephys.protocols.SweepProtocol):
    """Protocol consisting of step and holding current."""

    def __init__(
        self,
        name=None,
        step_stimuli=None,
        holding_stimulus=None,
        recordings=None,
        cvode_active=None,
        stochkv_det=None,
    ):
        """Constructor.

        Args:
            name (str): name of this object
            step_stimuli (list of Stimuli): List of Stimulus objects used in protocol
            holding_stimulus (Stimulus): holding stimulus
            recordings (list of Recordings): Recording objects used in the
                protocol
            cvode_active (bool): whether to use variable time step
            stochkv_det (bool): False to use stochasticity
        """
        super().__init__(
            name,
            stimuli=step_stimuli + [holding_stimulus]
            if holding_stimulus is not None
            else step_stimuli,
            recordings=recordings,
            cvode_active=cvode_active,
        )

        self.step_stimuli = step_stimuli
        self.holding_stimulus = holding_stimulus
        self.stochkv_det = stochkv_det

    def instantiate(self, sim=None, icell=None):
        """Instantiate."""
        for stimulus in self.stimuli:
            stimulus.instantiate(sim=sim, icell=icell)

        self.recordings = check_recordings(self.recordings, icell, sim)

        for recording in self.recordings:
            try:
                recording.instantiate(sim=sim, icell=icell)
            except ephys.locations.EPhysLocInstantiateException as e:
                logger.debug(
                    "SweepProtocol: Instantiating recording generated location "
                    "exception: %s, will return empty response for this recording",
                    e,
                )

    def run(self, cell_model, param_values, sim=None, isolate=None, timeout=None):
        """Run protocol."""
        responses = {}
        if self.stochkv_det is not None and not self.stochkv_det:
            for mechanism in cell_model.mechanisms:
                if "Stoch" in mechanism.prefix:
                    mechanism.deterministic = False
            self.cvode_active = False

        responses.update(
            super().run(cell_model, param_values, sim=sim, isolate=isolate)
        )

        if self.stochkv_det is not None and not self.stochkv_det:
            for mechanism in cell_model.mechanisms:
                if "Stoch" in mechanism.prefix:
                    mechanism.deterministic = True
            self.cvode_active = True

        return responses

    @property
    def stim_start(self):
        """Time stimulus starts."""
        return self.step_stimuli[0].step_delay

    @property
    def stim_duration(self):
        """Time stimulus duration."""
        return (
            self.step_stimuli[-1].step_delay
            + self.step_stimuli[-1].step_duration
            - self.step_stimuli[0].step_delay
        )

    @property
    def stim_end(self):
        """Time stimulus ends."""
        return self.step_stimuli[-1].step_delay + self.step_stimuli[-1].step_duration

    @property
    def stim_last_start(self):
        """Time stimulus last start."""
        return self.step_stimuli[-1].step_delay

    @property
    def step_amplitude(self):
        """Stimuli mean amplitude."""
        amplitudes = [step_stim.step_amplitude for step_stim in self.step_stimuli]

        if None in amplitudes:
            return None
        else:
            return numpy.mean(amplitudes)


class StepThresholdProtocol(StepProtocol):
    """Step protocol based on threshold."""

    def __init__(
        self,
        name,
        thresh_perc=None,
        step_stimuli=None,
        holding_stimulus=None,
        recordings=None,
        cvode_active=None,
        stochkv_det=None,
    ):
        """Constructor."""
        super().__init__(
            name,
            step_stimuli=step_stimuli,
            holding_stimulus=holding_stimulus,
            recordings=recordings,
            cvode_active=cvode_active,
            stochkv_det=stochkv_det,
        )

        self.thresh_perc = thresh_perc

    def run(self, cell_model, param_values, sim=None, isolate=None, timeout=None):
        """Run protocol."""
        responses = {}
        if not hasattr(cell_model, "threshold_current"):
            raise Exception(
                "StepThresholdProtocol: running on cell_model "
                f"that doesnt have threshold current value set: {str(cell_model)}"
            )

        for step_stim in self.step_stimuli:
            step_stim.step_amplitude = cell_model.threshold_current * (
                float(self.thresh_perc) / 100.0
            )

        self.holding_stimulus.step_amplitude = cell_model.holding_current

        responses.update(
            super().run(cell_model, param_values, sim=sim, isolate=isolate)
        )

        return responses


# Adjust accordingly
class RampProtocol(SweepProtocolCustom):
    """Protocol consisting of ramp and holding current."""

    def __init__(
        self,
        name=None,
        ramp_stimulus=None,
        holding_stimulus=None,
        recordings=None,
        cvode_active=None,
    ):
        """Constructor.

        Args:
            name (str): name of this object
            ramp_stimulus (list of Stimuli): Stimulus objects used in protocol
            holding_stimulus (Stimulus): holding stimulus
            recordings (list of Recordings): Recording objects used in the
                protocol
            cvode_active (bool): whether to use variable time step
        """
        super().__init__(
            name,
            stimuli=[ramp_stimulus, holding_stimulus]
            if holding_stimulus is not None
            else [ramp_stimulus],
            recordings=recordings,
            cvode_active=cvode_active,
        )

        self.ramp_stimulus = ramp_stimulus
        self.holding_stimulus = holding_stimulus

    @property
    def step_delay(self):
        """Time stimulus delay."""
        return self.ramp_stimulus.ramp_delay

    @property
    def step_duration(self):
        """Time stimulus duration."""
        return self.ramp_stimulus.ramp_duration


class RampThresholdProtocol(RampProtocol):
    """Step protocol based on threshold."""

    def __init__(
        self,
        name,
        thresh_perc_start=None,
        thresh_perc_end=None,
        ramp_stimulus=None,
        holding_stimulus=None,
        recordings=None,
        cvode_active=None,
    ):
        """Constructor."""
        super().__init__(
            name,
            ramp_stimulus=ramp_stimulus,
            holding_stimulus=holding_stimulus,
            recordings=recordings,
            cvode_active=cvode_active,
        )

        self.thresh_perc_start = thresh_perc_start
        self.thresh_perc_end = thresh_perc_end

    def run(self, cell_model, param_values, sim=None, isolate=None, timeout=None):
        """Run protocol."""
        responses = {}
        if not hasattr(cell_model, "threshold_current"):
            raise Exception(
                "RampThresholdProtocol: running on cell_model "
                f"that doesnt have threshold current value set: {str(cell_model)}"
            )

        self.ramp_stimulus.ramp_amplitude_start = cell_model.threshold_current * (
            float(self.thresh_perc_start) / 100
        )
        self.ramp_stimulus.ramp_amplitude_end = cell_model.threshold_current * (
            float(self.thresh_perc_end) / 100
        )

        self.holding_stimulus.step_amplitude = cell_model.holding_current

        responses.update(
            super().run(cell_model, param_values, sim=sim, isolate=isolate)
        )

        return responses
