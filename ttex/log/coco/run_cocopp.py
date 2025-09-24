import cocopp
from typing import List, Optional
import logging
import os
from contextlib import redirect_stdout
from cocopp.testbedsettings import Testbed, suite_to_testbed
from dataclasses import dataclass, field
from cocopp.dataformatsettings import BBOBNewDataFormat


def run_cocopp(
    result_paths: List[str], output_dir: Optional[str] = None, silent: bool = False
):
    """Run COCO post-processing on given result paths."""

    args = result_paths
    if output_dir is not None:
        args = ["-o", output_dir] + args
    args = " ".join(args)

    # Suppress DEBUG logs from matplotlib components
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("matplotlib.ticker").setLevel(logging.WARNING)
    logging.getLogger("matplotlib.backends.backend_pdf").setLevel(logging.WARNING)
    # Suppress INFO logs from fontTools components
    logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
    logging.getLogger("fontTools.ttLib").setLevel(logging.WARNING)

    if silent:
        with open(os.devnull, "w") as fnull:
            with redirect_stdout(fnull):
                res = cocopp.main(args)
    else:
        res = cocopp.main(args)

    return res


class MinimalTestbed(Testbed):
    settings = dict(
        name="MinimalTestbed",
        instances_are_uniform=False,
        reference_algorithm_filename=None,
        reference_algorithm_displayname=None,
        instancesOfInterest=None,  # None: consider all instances
        plots_on_main_html_page=[],
        data_format=BBOBNewDataFormat(),
        number_of_points=10,
        first_function_number=1,
        last_function_number=5,
    )

    def __init__(self, target_values):
        self.target_values = target_values
        self.ppfigdim_target_values = target_values
        for key, val in self.settings.items():
            setattr(self, key, val)


suite_to_testbed["minimal"] = "MinimalTestbed"
