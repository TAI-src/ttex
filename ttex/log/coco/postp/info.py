from dataclasses import dataclass
from typing import List
from cocopp.dataformatsettings import BBOBNewDataFormat


class FunctionInfo:
    def __init__(self, func_id: int, name: str, long_name: str):
        self.func_id = func_id
        self.name = name
        self.long_name = long_name

    def to_str(self, short: bool = False) -> str:
        if short:
            return f"{self.func_id} {self.name}"
        else:
            return f"{self.func_id} {self.long_name}"


@dataclass
class SuiteInfo:
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
