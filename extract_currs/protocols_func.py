"""Protocol-related functions."""

import json
import logging
import os

import bluepyopt.ephys as ephys

from extract_currs.protocols import (
    RampProtocol,
    RampThresholdProtocol,
    StepProtocol,
    StepThresholdProtocol,
    RatSSCxThresholdDetectionProtocol,
    RatSSCxRinHoldcurrentProtocol,
    RatSSCxMainProtocol,
    SweepProtocolCustom,
)
from extract_currs.recordings import RecordingCustom
from extract_currs.locations import (
    NrnSomaDistanceCompLocation,
    NrnSomaDistanceCompLocationApical,
)
from extract_currs.features import define_fitness_calculator
from extract_currs.stimuli import SAHP

logger = logging.getLogger(__name__)

soma_loc = ephys.locations.NrnSeclistCompLocation(
    name="soma", seclist_name="somatic", sec_index=0, comp_x=0.5
)


def read_sAHP_protocol(protocol_name, protocol_definition, recordings):
    """Read sAHP protocol from definition."""

    sahp_definition = protocol_definition["stimuli"]["sahp"]

    # assumes that holding.delay = 0 and holding.duration == sahp.totduration
    if "holding_current" in sahp_definition:
        holding_current = sahp_definition["holding_current"]
    elif "holding" in protocol_definition["stimuli"]:
        holding_current = protocol_definition["stimuli"]["holding"]["amp"]
    else:
        holding_current = 0.0

    sahp_stimulus = SAHP(
        delay=sahp_definition["delay"],
        totduration=sahp_definition["totduration"],
        # strange way to input amp, but Maria confirmed it.
        amp=sahp_definition["amp"] - sahp_definition["depol"],
        tmid=sahp_definition["delay"] + sahp_definition["duration_of_depol1"],
        tmid2=sahp_definition["delay"]
        + sahp_definition["duration"]
        - sahp_definition["duration_of_depol2"],
        toff=sahp_definition["delay"] + sahp_definition["duration"],
        long_amp=sahp_definition["depol"],
        holding_current=holding_current,
        location=soma_loc,
    )

    return SweepProtocolCustom(
        name=protocol_name,
        stimuli=[sahp_stimulus],
        recordings=recordings,
    )


# Adjust accordingly
def read_ramp_threshold_protocol(protocol_name, protocol_definition, recordings):
    """Read ramp threshold protocol from definition."""

    ramp_definition = protocol_definition["stimuli"]["ramp"]
    ramp_stimulus = ephys.stimuli.NrnRampPulse(
        ramp_delay=ramp_definition["ramp_delay"],
        ramp_duration=ramp_definition["ramp_duration"],
        location=soma_loc,
        total_duration=ramp_definition["totduration"],
    )

    holding_stimulus = ephys.stimuli.NrnSquarePulse(
        step_delay=0.0,
        step_duration=ramp_definition["totduration"],
        location=soma_loc,
        total_duration=ramp_definition["totduration"],
    )

    return RampThresholdProtocol(
        name=protocol_name,
        ramp_stimulus=ramp_stimulus,
        holding_stimulus=holding_stimulus,
        thresh_perc_start=ramp_definition["thresh_perc_start"],
        thresh_perc_end=ramp_definition["thresh_perc_end"],
        recordings=recordings,
    )


def read_ramp_protocol(protocol_name, protocol_definition, recordings):
    """Read ramp protocol from definition."""

    ramp_definition = protocol_definition["stimuli"]["ramp"]
    ramp_stimulus = ephys.stimuli.NrnRampPulse(
        ramp_amplitude_start=ramp_definition["ramp_amplitude_start"],
        ramp_amplitude_end=ramp_definition["ramp_amplitude_end"],
        ramp_delay=ramp_definition["ramp_delay"],
        ramp_duration=ramp_definition["ramp_duration"],
        location=soma_loc,
        total_duration=ramp_definition["totduration"],
    )

    if "holding" in protocol_definition["stimuli"]:
        holding_definition = protocol_definition["stimuli"]["holding"]
        holding_stimulus = ephys.stimuli.NrnSquarePulse(
            step_amplitude=holding_definition["amp"],
            step_delay=holding_definition["delay"],
            step_duration=holding_definition["duration"],
            location=soma_loc,
            total_duration=holding_definition["totduration"],
        )
    else:
        holding_stimulus = None

    return RampProtocol(
        name=protocol_name,
        ramp_stimulus=ramp_stimulus,
        holding_stimulus=holding_stimulus,
        recordings=recordings,
    )


def read_step_protocol(
    protocol_name, protocol_definition, recordings, stochkv_det=None, cvode_active=False
):
    """Read step protocol from definition."""

    step_definitions = protocol_definition["stimuli"]["step"]
    if isinstance(step_definitions, dict):
        step_definitions = [step_definitions]

    step_stimuli = []
    for step_definition in step_definitions:
        step_stim = ephys.stimuli.NrnSquarePulse(
            step_amplitude=step_definition["amp"],
            step_delay=step_definition["delay"],
            step_duration=step_definition["duration"],
            location=soma_loc,
            total_duration=step_definition["totduration"],
        )
        step_stimuli.append(step_stim)

    if "holding" in protocol_definition["stimuli"]:
        holding_definition = protocol_definition["stimuli"]["holding"]
        holding_stimulus = ephys.stimuli.NrnSquarePulse(
            step_amplitude=holding_definition["amp"],
            step_delay=holding_definition["delay"],
            step_duration=holding_definition["duration"],
            location=soma_loc,
            total_duration=holding_definition["totduration"],
        )
    else:
        holding_stimulus = None

    if stochkv_det is None:
        stochkv_det = (
            step_definition["stochkv_det"] if "stochkv_det" in step_definition else None
        )

    return StepProtocol(
        name=protocol_name,
        step_stimuli=step_stimuli,
        holding_stimulus=holding_stimulus,
        recordings=recordings,
        stochkv_det=stochkv_det,
        cvode_active=cvode_active,
    )


def read_step_threshold_protocol(
    protocol_name, protocol_definition, recordings, stochkv_det=None
):
    """Read step threshold protocol from definition."""

    step_definitions = protocol_definition["stimuli"]["step"]
    if isinstance(step_definitions, dict):
        step_definitions = [step_definitions]

    step_stimuli = []
    for step_definition in step_definitions:
        step_stim = ephys.stimuli.NrnSquarePulse(
            step_delay=step_definition["delay"],
            step_duration=step_definition["duration"],
            location=soma_loc,
            total_duration=step_definition["totduration"],
        )
        step_stimuli.append(step_stim)

    holding_stimulus = ephys.stimuli.NrnSquarePulse(
        step_delay=0.0,
        step_duration=step_definition["totduration"],
        location=soma_loc,
        total_duration=step_definition["totduration"],
    )

    if stochkv_det is None:
        stochkv_det = (
            step_definition["stochkv_det"] if "stochkv_det" in step_definition else None
        )

    return StepThresholdProtocol(
        name=protocol_name,
        step_stimuli=step_stimuli,
        holding_stimulus=holding_stimulus,
        thresh_perc=step_definition["thresh_perc"],
        recordings=recordings,
        stochkv_det=stochkv_det,
    )


def define_protocols(
    protocols_filename,
    var_list,
    stochkv_det=None,
    runopt=False,
    prefix="",
    apical_point_isec=None,
    stage=None,
    do_simplify_morph=False,
):
    """Define protocols."""

    with open(os.path.join(protocols_filename)) as protocol_file:
        protocol_definitions = json.load(protocol_file)

    if "__comment" in protocol_definitions:
        del protocol_definitions["__comment"]

    protocols_dict = {}

    for protocol_name, protocol_definition in protocol_definitions.items():

        if ("stage" in protocol_definition) and (stage is not None) and (stage > 0):
            if stage not in protocol_definition["stage"]:
                continue  # protocol not used in this stage

        if protocol_name not in ["Main", "RinHoldcurrent"]:
            # changed here
            recordings = []
            for var in var_list:
                recordings.append(
                    RecordingCustom(
                        name="%s.%s.soma.%s" % (prefix, protocol_name, var),
                        location=soma_loc,
                        variable=var,
                    )
                )

            if "extra_recordings" in protocol_definition:
                for recording_definition in protocol_definition["extra_recordings"]:
                    if recording_definition["type"] == "somadistance":
                        location = NrnSomaDistanceCompLocation(
                            name=recording_definition["name"],
                            soma_distance=recording_definition["somadistance"],
                            seclist_name=recording_definition["seclist_name"],
                            do_simplify_morph=do_simplify_morph,
                        )

                    elif recording_definition["type"] == "somadistanceapic":
                        location = NrnSomaDistanceCompLocationApical(
                            name=recording_definition["name"],
                            soma_distance=recording_definition["somadistance"],
                            seclist_name=recording_definition["seclist_name"],
                            apical_point_isec=apical_point_isec,
                            do_simplify_morph=do_simplify_morph,
                        )

                    elif recording_definition["type"] == "nrnseclistcomp":
                        location = ephys.locations.NrnSeclistCompLocation(
                            name=recording_definition["name"],
                            comp_x=recording_definition["comp_x"],
                            sec_index=recording_definition["sec_index"],
                            seclist_name=recording_definition["seclist_name"],
                        )

                    else:
                        raise Exception(
                            "Recording type %s not supported"
                            % recording_definition["type"]
                        )

                    # changed here
                    for var in var_list:
                        recording = RecordingCustom(
                            name="%s.%s.%s.%s"
                            % (prefix, protocol_name, location.name, var),
                            location=location,
                            variable=var,
                        )
                        recordings.append(recording)

            if (
                "type" in protocol_definition
                and protocol_definition["type"] == "StepProtocol"
            ):
                protocols_dict[protocol_name] = read_step_protocol(
                    protocol_name, protocol_definition, recordings, stochkv_det
                )
            elif (
                "type" in protocol_definition
                and protocol_definition["type"] == "StepThresholdProtocol"
            ):
                protocols_dict[protocol_name] = read_step_threshold_protocol(
                    protocol_name, protocol_definition, recordings, stochkv_det
                )
            elif (
                "type" in protocol_definition
                and protocol_definition["type"] == "RampThresholdProtocol"
            ):
                protocols_dict[protocol_name] = read_ramp_threshold_protocol(
                    protocol_name, protocol_definition, recordings
                )
            elif (
                "type" in protocol_definition
                and protocol_definition["type"] == "RampProtocol"
            ):
                protocols_dict[protocol_name] = read_ramp_protocol(
                    protocol_name, protocol_definition, recordings
                )
            elif (
                "type" in protocol_definition
                and protocol_definition["type"] == "SAHPProtocol"
            ):
                protocols_dict[protocol_name] = read_sAHP_protocol(
                    protocol_name, protocol_definition, recordings
                )
            elif (
                "type" in protocol_definition
                and protocol_definition["type"] == "RatSSCxThresholdDetectionProtocol"
            ):
                protocols_dict[
                    "ThresholdDetection"
                ] = RatSSCxThresholdDetectionProtocol(
                    "IDRest",
                    step_protocol_template=read_step_protocol(
                        "Threshold", protocol_definition["step_template"], recordings
                    ),
                    prefix=prefix,
                )
            else:
                stimuli = []
                for stimulus_definition in protocol_definition["stimuli"]:
                    stimuli.append(
                        ephys.stimuli.NrnSquarePulse(
                            step_amplitude=stimulus_definition["amp"],
                            step_delay=stimulus_definition["delay"],
                            step_duration=stimulus_definition["duration"],
                            location=soma_loc,
                            total_duration=stimulus_definition["totduration"],
                        )
                    )

                protocols_dict[protocol_name] = SweepProtocolCustom(
                    name=protocol_name, stimuli=stimuli, recordings=recordings
                )

    if "Main" in protocol_definitions.keys():

        protocols_dict["RinHoldcurrent"] = RatSSCxRinHoldcurrentProtocol(
            "RinHoldCurrent",
            rin_protocol_template=protocols_dict["Rin"],
            holdi_precision=protocol_definitions["RinHoldcurrent"]["holdi_precision"],
            holdi_max_depth=protocol_definitions["RinHoldcurrent"]["holdi_max_depth"],
            prefix=prefix,
        )

        other_protocols = []

        for protocol_name in protocol_definitions["Main"]["other_protocols"]:
            if protocol_name in protocols_dict:
                other_protocols.append(protocols_dict[protocol_name])

        pre_protocols = []
        preprot_score_threshold = 1

        if "pre_protocols" in protocol_definitions["Main"]:
            for protocol_name in protocol_definitions["Main"]["pre_protocols"]:
                pre_protocols.append(protocols_dict[protocol_name])
            preprot_score_threshold = protocol_definitions["Main"][
                "preprot_score_threshold"
            ]

        protocols_dict["Main"] = RatSSCxMainProtocol(
            "Main",
            rmp_protocol=protocols_dict["RMP"],
            rmp_score_threshold=protocol_definitions["Main"]["rmp_score_threshold"],
            rinhold_protocol=protocols_dict["RinHoldcurrent"],
            rin_score_threshold=protocol_definitions["Main"]["rin_score_threshold"],
            thdetect_protocol=protocols_dict["ThresholdDetection"],
            other_protocols=other_protocols,
            pre_protocols=pre_protocols,
            preprot_score_threshold=preprot_score_threshold,
            use_rmp_rin_thresholds=runopt,
        )

    return protocols_dict


def get_apical_point_data(recipe, etypetest, morph):
    """Return filename and apical points list from file."""
    if recipe and ("morph_path" in recipe) and etypetest is not None:
        # use direct path
        morph_path = recipe["morph_path"]
    else:
        # if not testing the morph must have been copied here before!
        morph_path = "morphologies/"

    basename = os.path.basename(morph)
    filename = os.path.splitext(basename)[0]
    morph = os.path.join(morph_path, basename)

    try:
        apsec_file = os.path.join(morph_path, "apical_points_isec.json")
        apical_points_isecs = json.load(open(apsec_file))
        logger.debug("Reading %s", apsec_file)

        return filename, apical_points_isecs
    except FileNotFoundError:
        return "", []


def create_protocols(
    etype,
    var_list,
    recipe_path="",
    stochkv_det=None,
    usethreshold=False,
    runopt=False,
    altmorph=None,
    etypetest=None,
    stage=None,
    do_simplify_morph=False,
    use_powertransform=False,
    prot_path="",
    apical_point_isec=None,
    features_path="",
):
    """Return a dict containing protocols.

    Args:
        etype (str): emodel. is taken from recipe if usethreshold and 'mm_test_recipe' in recipe
        var_list (list of str): list of variables (v, ina_NaTg, etc.) to record.
        recipe_path (str): path to recipe path. Not mandatory.
        stochkv_det (bool): set if stochastic or deterministic
        usethreshold (bool): set to True to take etype from recipe file.
        runopt (bool): is used as use_rmp_rin_thresholds in RatSSCxMainProtocol
        altmorph (list of lists containing the following):
            morphname -> morphology name to put in output files (can be '_')
            morph -> morphology file name
            apical_point_isec (optional) -> index of apical point section
        etypetest (str): if not None and altmorph is None: get morph_path from recipe
        stage (int): protocol stage.
        do_simplify_morph (bool): if True, set apical point to None and simplify morph in locations
        use_powertransform (bool): used in eFELFeatureExtra

        prot_path (str): protocol path. if not set, is taken from recipe.
        features_path (str): feature path. if not set, is taken from recipe.
    """
    if recipe_path:
        with open(os.path.join(recipe_path)) as f:
            recipes = json.load(f)
        recipe = recipes[etype]
    else:
        recipe = None

    if usethreshold:
        if recipe and "mm_test_recipe" in recipe:
            etype = recipe["mm_test_recipe"]
        else:
            if "_legacy" in etype:
                etype = etype.replace("_legacy", "")
            if "_combined" in etype:
                etype = etype.replace("_combined", "")

    if recipe and "use_powertransform" in recipe:
        use_powertransform = recipe["use_powertransform"]

    if recipe and not prot_path:
        prot_path = recipe["protocol"]

    if recipe and not features_path:
        features_path = recipe["features"]

    if altmorph is None:
        # get morphologies, convert to list if not given as list
        morphs = recipe["morphology"]
        if not isinstance(morphs, (list)):
            morphs = [["_", morphs]]
    elif not isinstance(altmorph, (list)):
        # use directly, either given as absolute or relative
        morphs = [["alt", altmorph]]
    else:
        morphs = altmorph

    for morphval in morphs:

        if len(morphval) == 3:
            morphname, morph, apical_point_isec0 = morphval
        else:
            morphname, morph = morphval
            apical_point_isec0 = None

        # get apical point isec if a directory is given!
        if apical_point_isec is None and (altmorph is None):
            filename, apical_points_isecs = get_apical_point_data(
                recipe, etypetest, morph
            )
            if filename in apical_points_isecs:
                apical_point_isec = int(apical_points_isecs[filename])

        if do_simplify_morph:
            apical_point_isec = None
        else:
            # check if apical point section should be overridden
            if apical_point_isec0 is not None:
                apical_point_isec = apical_point_isec0
                logger.debug("Apical point override with %d", apical_point_isec)

            if apical_point_isec is not None:
                logger.debug("Apical point at apical[%d]", apical_point_isec)

        protocols_dict = define_protocols(
            prot_path,
            var_list,
            stochkv_det,
            runopt,
            morphname,
            apical_point_isec,
            stage,
            do_simplify_morph,
        )

        if "Main" in protocols_dict.keys():

            fitness_calculator, efeatures = define_fitness_calculator(
                protocols_dict["Main"],
                features_path,
                morphname,
                stage,
                use_powertransform,
            )

            protocols_dict["Main"].fitness_calculator = fitness_calculator

            protocols_dict["Main"].rmp_efeature = efeatures[
                morphname + ".RMP.soma.v.voltage_base"
            ]

            protocols_dict["Main"].rin_efeature = efeatures[
                morphname + ".Rin.soma.v.ohmic_input_resistance_vb_ssse"
            ]

            protocols_dict["Main"].rin_efeature.stimulus_current = protocols_dict[
                "Main"
            ].rinhold_protocol.rin_protocol_template.step_amplitude

            # delete from this
            protocols_dict["RinHoldcurrent"].voltagebase_efeature = efeatures[
                morphname + ".Rin.soma.v.voltage_base"
            ]
            protocols_dict["ThresholdDetection"].holding_voltage = efeatures[
                morphname + ".Rin.soma.v.voltage_base"
            ].exp_mean
            # to this ??

            fitness_protocols = {"main_protocol": protocols_dict["Main"]}

        else:
            fitness_protocols = protocols_dict

    return fitness_protocols
