"""Output related functions."""

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def write_output(responses, output_dir):
    """Save each response in a file. Float-like responses are skipped."""
    # create output directory if not existent yet
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for key, resp in responses.items():
        if "holding_current" in key or "threshold_current" in key:
            logger.debug("{} : {}".format(key, resp))
        else:
            output_path = Path(output_dir) / f"{key}.dat"

            time = np.array(resp["time"])
            data = np.array(resp["voltage"])  # can be voltage or current

            np.savetxt(output_path, np.transpose(np.vstack((time, data))))
