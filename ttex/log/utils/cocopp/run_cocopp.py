import logging
import os
from contextlib import redirect_stdout

import cocopp

from ttex.log.utils.cocopp.info import SuiteInfo
from ttex.log.utils.cocopp.testbed import TestbedFactory


def run_cocopp(
    result_paths: list[str],
    suite_info: SuiteInfo,
    output_dir: str | None = None,
    silent: bool = False,
):
    """Run COCO post-processing on given result paths."""

    args = result_paths
    if output_dir is not None:
        args = ["-o", output_dir] + args
    args_str = " ".join(args)

    # Suppress DEBUG logs from matplotlib components
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("matplotlib.ticker").setLevel(logging.WARNING)
    logging.getLogger("matplotlib.backends.backend_pdf").setLevel(logging.WARNING)
    # Suppress INFO logs from fontTools components
    logging.getLogger("fontTools.subset").setLevel(logging.WARNING)
    logging.getLogger("fontTools.ttLib").setLevel(logging.WARNING)

    ## Create and register testbedsettings for cocopp based on suite info
    TestbedFactory.create_testbed_class(suite_info)

    if silent:
        with open(os.devnull, "w") as fnull, redirect_stdout(fnull):
            res = cocopp.main(args_str)
    else:
        res = cocopp.main(args_str)

    return res
