import cocopp
from typing import List, Optional
import logging
import os
from contextlib import redirect_stdout
from cocopp.testbedsettings import Testbed, suite_to_testbed
from dataclasses import dataclass, field
from cocopp.dataformatsettings import BBOBNewDataFormat
import numpy as np


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
        plots_on_main_html_page=[
            "pprldmany_02D_noiselessall.svg",
        ],
        data_format=BBOBNewDataFormat(),
        number_of_points=10,
        first_function_number=1,
        last_function_number=5,
        ppfigdim_target_values=(10, 1, 1e-1, 1e-2, 1e-3, 1e-5, 1e-8),
        scenario="rlbased",
        goto_dimension=2,
        rldDimsOfInterest=[2],
        short_names={1: "f1", 2: "f2", 3: "f3", 4: "f4", 5: "f5"},
        dimensions_to_display=[2],
        functions_with_legend=(1, 24),
        pptable_ftarget=1e-8,
        pptable_targetsOfInterest=(10, 1),
        pprldistr_target_values=(10.0, 1e-1, 1e-4, 1e-8),
        ppfvdistr_min_target=1e-8,
        pprldmany_target_values=10 ** np.arange(2, -8.2, -0.2),
        hardesttargetlatex="10^{-8}",
        pprldmany_target_range_latex="$10^{[-8..2]}$",
    )

    def __init__(self, target_values):
        # self.target_values = target_values
        # self.ppfigdim_target_values = target_values
        for key, val in self.settings.items():
            setattr(self, key, val)
        self.instantiate_attributes(target_values)


suite_to_testbed["minimal"] = "MinimalTestbed"
