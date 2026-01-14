from dataclasses import dataclass, field
from cocopp.dataformatsettings import BBOBNewDataFormat
import numpy as np
from typing import Dict, Optional, List
from ttex.log.coco.postp.info import FunctionInfo


@dataclass
class TestBedSettings:
    name: str
    dimensions: List[int]
    function_infos: List[FunctionInfo]
    number_of_points = 5  # number of points in log-scale plots (per decade)
    max_target = 2  # exponent of maximum target value for postprocessing
    min_target = -8  # exponent of minimum target value for postprocessing

    def __post_init__(self):
        # defaults based on ttex implementation
        self.instances_are_uniform = False
        self.reference_algorithm_filename = None
        self.reference_algorithm_displayname = None
        self.instancesOfInterest = None  # None: consider all instances
        self.data_format = BBOBNewDataFormat()
        self.scenario = "rlbased"

        ## Dimensions
        self.plots_on_main_html_page = [
            f"pprldmany_{dim}D_noiselessall.svg" for dim in self.dimensions
        ]
        self.goto_dimension = min(
            self.dimensions
        )  # auto-focus on smalles dimension in html
        self.rldDimsOfInterest = self.dimensions
        self.dimensions_to_display = self.dimensions

        ## Functions
        self.short_names: Dict[int, str] = {
            info.func_id: info.name for info in self.function_infos
        }
        self.first_function_number = min(self.short_names.keys())
        self.last_function_number = max(self.short_names.keys())
        self.functions_with_legend = (
            self.first_function_number,
            self.last_function_number,
        )

        # Targets
        self.pptable_ftarget = (
            10**self.min_target
        )  # value for determining the success ratio in all tables
        self.ppfvdistr_min_target = 10**self.min_target
        # high level targets
        few_targets = [
            10**exp for exp in range(self.max_target, self.min_target - 1, -1)
        ]
        many_targets = [
            10**exp for exp in np.arange(self.max_target, self.min_target - 0.2, -0.2)
        ]
        self.pptable_targetsOfInterest = tuple(few_targets)
        self.ppfig_target_values = tuple(few_targets)
        self.pprldistr_target_values = tuple(few_targets)
        self.pprldmany_target_values = tuple(many_targets)
        self.hardesttargetlatex = f"$10^{{{self.min_target}}}$"
        self.pprldmany_target_range_latex = (
            f"$10^{{[{self.min_target}..{self.max_target}]}}$"
        )
