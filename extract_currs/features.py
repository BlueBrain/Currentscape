"""Feature-related classes."""

import json
import logging

from bluepyopt.ephys.efeatures import eFELFeature

logger = logging.getLogger(__name__)


def define_efeatures(main_protocol, features_filename, prefix=""):
    """Define fitness calculator."""

    with open(features_filename) as features_file:
        feature_definitions = json.load(features_file)

    if "__comment" in feature_definitions:
        del feature_definitions["__comment"]

    efeatures = {}
    features = []

    for protocol_name, locations in feature_definitions.items():
        for recording_name, feature_configs in locations.items():
            for feature_config in feature_configs:

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

                feature = eFELFeature(
                    feature_name,
                    efel_feature_name=efel_feature_name,
                    recording_names=recording_names,
                    stim_start=stim_start,
                    stim_end=stim_end,
                    exp_mean=meanstd[0],
                    exp_std=meanstd[1],
                    stimulus_current=stimulus_current,
                    threshold=threshold,
                    int_settings={"strict_stiminterval": strict_stim},
                )
                efeatures[feature_name] = feature
                features.append(feature)

    return efeatures
