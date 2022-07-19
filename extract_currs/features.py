"""Feature-related classes."""

import json
import logging
import numpy

import bluepyopt.ephys as ephys
from bluepyopt.ephys.efeatures import eFELFeature
from bluepyopt.ephys.objectives import (
    SingletonObjective,
    EFeatureObjective,
    MaxObjective,
)
import efel

from extract_currs.YeoJohnson import YeoJohnson

logger = logging.getLogger(__name__)


# boxcox function
def clip_ld_convert(vals, shift, ld):
    """convert values with lambda."""

    vals = numpy.atleast_1d(vals)
    yj = YeoJohnson()

    if shift is not False:
        vals_bc = numpy.array(yj.fit(vals, ld))
    else:
        vals_bc = False

    return vals_bc


class eFELFeatureExtra(eFELFeature):
    """EFEL feature extra."""

    SERIALIZED_FIELDS = (
        "name",
        "efel_feature_name",
        "recording_names",
        "stim_start",
        "stim_end",
        "exp_mean",
        "exp_std",
        "threshold",
        "comment",
    )

    def __init__(
        self,
        name,
        efel_feature_name=None,
        recording_names=None,
        stim_start=None,
        stim_end=None,
        exp_mean=None,
        exp_std=None,
        exp_vals=None,
        threshold=None,
        stimulus_current=None,
        comment="",
        interp_step=None,
        double_settings=None,
        int_settings=None,
        prefix="",
        use_powertransform=False,
    ):
        """Constructor.

        Args:
            name (str): name of the eFELFeature object
            efel_feature_name (str): name of the eFeature in the eFEL library
                (ex: 'AP1_peak')
            recording_names (dict): eFEL features can accept several recordings
                as input
            stim_start (float): stimulation start time (ms)
            stim_end (float): stimulation end time (ms)
            exp_mean (float): experimental mean of this eFeature
            exp_std(float): experimental standard deviation of this eFeature
            threshold(float): spike detection threshold (mV)
            comment (str): comment
        """

        super(eFELFeatureExtra, self).__init__(
            name,
            efel_feature_name,
            recording_names,
            stim_start,
            stim_end,
            exp_mean,
            exp_std,
            threshold,
            stimulus_current,
            comment,
            interp_step,
            double_settings,
            int_settings,
        )

        extra_features = [
            "spikerate_tau_jj_skip",
            "spikerate_drop_skip",
            "spikerate_tau_log_skip",
            "spikerate_tau_fit_skip",
        ]

        if self.efel_feature_name in extra_features:
            self.extra_feature_name = self.efel_feature_name
            self.efel_feature_name = "peak_time"
        else:
            self.extra_feature_name = None

        self.prefix = prefix
        self.exp_vals = exp_vals
        self.use_powertransform = use_powertransform

    def get_bpo_feature(self, responses):
        """Return internal feature which is directly passed as a response."""

        if (self.prefix + "." + self.efel_feature_name) not in responses:
            return None
            # raise Exception(
            #     'Internal BluePyOpt feature %s not set '% self.efel_feature_name)
        else:
            return responses[self.prefix + "." + self.efel_feature_name]

    def get_bpo_score(self, responses):
        """Return internal score which is directly passed as a response."""

        feature_value = self.get_bpo_feature(responses)
        if feature_value is None:
            score = 250.0
        else:
            score = abs(feature_value - self.exp_mean) / self.exp_std
        return score

    def calculate_features(self, responses, raise_warnings=False):
        """Calculate feature value."""

        if self.efel_feature_name.startswith("bpo_"):  # check if internal feature
            feature_values = numpy.array(self.get_bpo_feature(responses))
        else:
            efel_trace = self._construct_efel_trace(responses)

            if efel_trace is None:
                feature_values = None
            else:
                self._setup_efel()

                values = efel.getFeatureValues(
                    [efel_trace],
                    [self.efel_feature_name],
                    raise_warnings=raise_warnings,
                )

                feature_values = values[0][self.efel_feature_name]

                efel.reset()

        logger.debug("Calculated values for %s: %s", self.name, str(feature_values))

        return feature_values

    def calculate_score(self, responses, trace_check=False):
        """Calculate the score."""

        if self.efel_feature_name.startswith("bpo_"):  # check if internal feature
            score = self.get_bpo_score(responses)

        elif self.exp_mean is None:
            score = 0

        else:

            feature_values = self.calculate_features(responses)
            if (feature_values is None) or (len(feature_values) == 0):
                score = 250.0
            else:
                if (len(self.exp_vals) == 2) or (self.use_powertransform is False):
                    # assume gaussian, use no conversion
                    score = (
                        numpy.sum(numpy.fabs(feature_values - self.exp_mean))
                        / self.exp_std
                        / len(feature_values)
                    )
                    logger.debug("Calculated score for %s: %f", self.name, score)

                elif len(self.exp_vals) == 6:
                    # use boxcox/yeojohnson
                    [_, _, m, s, ld, shift] = self.exp_vals
                    val_bc = clip_ld_convert(feature_values, shift, ld)
                    score = numpy.sum(numpy.fabs(val_bc - m)) / s / len(feature_values)
                    logger.debug(
                        "Calculated score for %s: %f using boxcox/yeojohnson val: %s, m:%f, s:%f",
                        self.name,
                        score,
                        val_bc,
                        m,
                        s,
                    )

        return score


class SingletonWeightObjective(EFeatureObjective):
    """Single EPhys feature."""

    def __init__(self, name, feature, weight):
        """Constructor.

        Args:
            name (str): name of this object
            features (EFeature): single eFeature inside this objective
        """

        super(SingletonWeightObjective, self).__init__(name, [feature])
        self.weight = weight

    def calculate_score(self, responses):
        """Objective score."""

        return self.calculate_feature_scores(responses)[0] * self.weight

    def __str__(self):
        """String representation."""

        return "( %s ), weight:%f" % (self.features[0], self.weight)


def define_fitness_calculator(
    main_protocol, features_filename, prefix="", stage=None, use_powertransform=False
):
    """Define fitness calculator."""

    with open(features_filename) as features_file:
        feature_definitions = json.load(features_file)

    if "__comment" in feature_definitions:
        del feature_definitions["__comment"]

    objectives = []
    efeatures = {}
    features = []

    for protocol_name, locations in feature_definitions.items():
        for recording_name, feature_configs in locations.items():
            for feature_config in feature_configs:

                if ("stage" in feature_config) and (stage is not None) and (stage > 0):
                    if stage not in feature_config["stage"]:
                        continue  # feature not used in this stage

                efel_feature_name = feature_config["feature"]
                meanstd = feature_config["val"]

                if hasattr(main_protocol, "subprotocols"):
                    protocol = main_protocol.subprotocols()[protocol_name]
                else:
                    protocol = main_protocol[protocol_name]

                feature_name = "%s.%s.%s.%s" % (
                    prefix,
                    protocol_name,
                    recording_name,
                    efel_feature_name,
                )
                recording_names = {
                    "": "%s.%s.%s" % (prefix, protocol_name, recording_name)
                }

                if "weight" in feature_config:
                    weight = feature_config["weight"]
                else:
                    weight = 1

                if "strict_stim" in feature_config:
                    strict_stim = feature_config["strict_stim"]
                else:
                    strict_stim = True

                if hasattr(protocol, "stim_start"):

                    stim_start = protocol.stim_start

                    if "threshold" in feature_config:
                        threshold = feature_config["threshold"]
                    else:
                        threshold = -30

                    if "bAP" in protocol_name:
                        # bAP response can be after stimulus
                        stim_end = protocol.total_duration
                    elif "H40S8" in protocol_name:
                        stim_end = protocol.stim_last_start
                    else:
                        stim_end = protocol.stim_end

                    stimulus_current = protocol.step_amplitude

                else:
                    stim_start = None
                    stim_end = None
                    stimulus_current = None
                    threshold = None

                feature = eFELFeatureExtra(
                    feature_name,
                    efel_feature_name=efel_feature_name,
                    recording_names=recording_names,
                    stim_start=stim_start,
                    stim_end=stim_end,
                    exp_mean=meanstd[0],
                    exp_std=meanstd[1],
                    exp_vals=meanstd,
                    stimulus_current=stimulus_current,
                    threshold=threshold,
                    prefix=prefix,
                    int_settings={"strict_stiminterval": strict_stim},
                    use_powertransform=use_powertransform,
                )
                efeatures[feature_name] = feature
                features.append(feature)
                objective = SingletonWeightObjective(feature_name, feature, weight)
                objectives.append(objective)

    # objectives.append(MaxObjective('global_maximum', features))
    fitcalc = ephys.objectivescalculators.ObjectivesCalculator(objectives)

    return fitcalc, efeatures
