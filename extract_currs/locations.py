"""Location classes."""

import logging

from bluepyopt import ephys

logger = logging.getLogger(__name__)


def multi_locations(sectionlist):
    """Define mechanisms."""
    if sectionlist == "alldend":
        seclist_locs = [
            ephys.locations.NrnSeclistLocation("apical", seclist_name="apical"),
            ephys.locations.NrnSeclistLocation("basal", seclist_name="basal"),
        ]
    elif sectionlist == "somadend":
        seclist_locs = [
            ephys.locations.NrnSeclistLocation("apical", seclist_name="apical"),
            ephys.locations.NrnSeclistLocation("basal", seclist_name="basal"),
            ephys.locations.NrnSeclistLocation("somatic", seclist_name="somatic"),
        ]
    elif sectionlist == "somaxon":
        seclist_locs = [
            ephys.locations.NrnSeclistLocation("axonal", seclist_name="axonal"),
            ephys.locations.NrnSeclistLocation("somatic", seclist_name="somatic"),
        ]
    elif sectionlist == "allact":
        seclist_locs = [
            ephys.locations.NrnSeclistLocation("apical", seclist_name="apical"),
            ephys.locations.NrnSeclistLocation("basal", seclist_name="basal"),
            ephys.locations.NrnSeclistLocation("somatic", seclist_name="somatic"),
            ephys.locations.NrnSeclistLocation("axonal", seclist_name="axonal"),
        ]
    else:
        seclist_locs = [
            ephys.locations.NrnSeclistLocation(sectionlist, seclist_name=sectionlist)
        ]

    return seclist_locs


class NrnSomaDistanceCompLocation(ephys.locations.NrnSomaDistanceCompLocation):
    """Location at a given distance from soma."""

    def __init__(
        self,
        name,
        soma_distance=None,
        seclist_name=None,
        comment="",
        do_simplify_morph=False,
    ):
        """Constructor."""
        super().__init__(name, soma_distance, seclist_name, comment)
        self.do_simplify_morph = do_simplify_morph

    def instantiate(self, sim=None, icell=None):
        """Find the instantiate compartment."""
        soma = icell.soma[0]

        sim.neuron.h.distance(0, 0.5, sec=soma)

        iseclist = getattr(icell, self.seclist_name)

        icomp = None

        for isec in iseclist:
            start_distance = sim.neuron.h.distance(1, 0.0, sec=isec)
            end_distance = sim.neuron.h.distance(1, 1.0, sec=isec)

            min_distance = min(start_distance, end_distance)
            max_distance = max(start_distance, end_distance)

            if min_distance <= self.soma_distance <= end_distance:
                comp_x = float(self.soma_distance - min_distance) / (
                    max_distance - min_distance
                )

                if self.do_simplify_morph:
                    isec.nseg = 1 + 2 * int(isec.L / 40.0)
                icomp = isec(comp_x)
                seccomp = isec
                break

        if icomp is None:
            raise ephys.locations.EPhysLocInstantiateException(
                f"No comp found at {self.soma_distance} distance from soma"
            )

        logger.debug(
            "Using %s at distance %f, nseg %f, length %f",
            icomp,
            sim.neuron.h.distance(1, comp_x, sec=seccomp),
            seccomp.nseg,
            end_distance - start_distance,
        )

        return icomp


class NrnSomaDistanceCompLocationApical(ephys.locations.NrnSomaDistanceCompLocation):
    """Location in the apical branch at a given distance from soma."""

    def __init__(
        self,
        name,
        soma_distance=None,
        seclist_name=None,
        comment="",
        apical_point_isec=None,
        do_simplify_morph=False,
    ):
        """Constructor."""
        super().__init__(name, soma_distance, seclist_name, comment)
        self.apical_point_isec = apical_point_isec
        self.do_simplify_morph = do_simplify_morph

    def instantiate(self, sim=None, icell=None):
        """Find the instantiate compartment."""
        # pylint: disable=too-many-locals, too-many-branches
        if self.do_simplify_morph:

            soma = icell.soma[0]

            sim.neuron.h.distance(0, 0.5, sec=soma)

            iseclist = getattr(icell, self.seclist_name)

            icomp = None

            for isec in iseclist:
                start_distance = sim.neuron.h.distance(1, 0.0, sec=isec)
                end_distance = sim.neuron.h.distance(1, 1.0, sec=isec)

                min_distance = min(start_distance, end_distance)
                max_distance = max(start_distance, end_distance)

                if min_distance <= self.soma_distance <= end_distance:

                    comp_x = float(self.soma_distance - min_distance) / (
                        max_distance - min_distance
                    )

                    isec.nseg = 1 + 2 * int(isec.L / 100.0)
                    icomp = isec(comp_x)
                    seccomp = isec
                    break

            if icomp is None:
                raise ephys.locations.EPhysLocInstantiateException(
                    f"No comp found at {self.soma_distance} distance from soma"
                )

            logger.debug(
                "Using %s at distance %f, nseg %f, length %f",
                icomp,
                sim.neuron.h.distance(1, comp_x, sec=seccomp),
                seccomp.nseg,
                end_distance - start_distance,
            )

        else:
            if self.apical_point_isec is None:
                raise ephys.locations.EPhysLocInstantiateException(
                    "No apical point was given"
                )

            apical_branch = []
            section = icell.apic[self.apical_point_isec]
            while True:
                name = str(section.name()).rsplit(".", maxsplit=1)[-1]
                if "soma[0]" == name:
                    break
                apical_branch.append(section)

                if sim.neuron.h.SectionRef(sec=section).has_parent():
                    section = sim.neuron.h.SectionRef(sec=section).parent
                else:
                    raise ephys.locations.EPhysLocInstantiateException(
                        "soma[0] was not reached from apical point"
                    )

            soma = icell.soma[0]

            sim.neuron.h.distance(0, 0.5, sec=soma)

            icomp = None

            for isec in apical_branch:
                start_distance = sim.neuron.h.distance(1, 0.0, sec=isec)
                end_distance = sim.neuron.h.distance(1, 1.0, sec=isec)

                min_distance = min(start_distance, end_distance)
                max_distance = max(start_distance, end_distance)

                if min_distance <= self.soma_distance <= end_distance:
                    comp_x = float(self.soma_distance - min_distance) / (
                        max_distance - min_distance
                    )

                    icomp = isec(comp_x)
                    seccomp = isec

            if icomp is None:
                raise ephys.locations.EPhysLocInstantiateException(
                    f"No comp found at {self.soma_distance} distance from soma"
                )

            logger.debug(
                "Using %s at distance %f",
                icomp,
                sim.neuron.h.distance(1, comp_x, sec=seccomp),
            )

        return icomp
