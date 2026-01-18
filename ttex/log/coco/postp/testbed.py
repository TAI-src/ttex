from dataclasses import dataclass, field
import numpy as np
from typing import Dict, Optional, List
from ttex.log.coco.postp.info import FunctionInfo, SuiteInfo
from cocopp.testbedsettings import Testbed, suite_to_testbed
import cocopp.testbedsettings as tbs


class TestBedSettings:

    def __init__(self, suite_info: SuiteInfo):
        self.suite_info = suite_info
        self.settings = TestBedSettings._create_settings_dict(suite_info)

    @staticmethod
    def _create_settings_dict(suite_info: SuiteInfo) -> dict:
        suite_settings = dict(
            name=suite_info.name,
            instances_are_uniform=suite_info.instances_are_uniform,
            reference_algorithm_filename=suite_info.reference_algorithm_filename,
            reference_algorithm_displayname=suite_info.reference_algorithm_displayname,
            instancesOfInterest=suite_info.instancesOfInterest,
            data_format=suite_info.data_format,
            scenario=suite_info.scenario,
        )
        dim_settings = dict(
            plots_on_main_html_page=[
                f"pprldmany_{dim}D_noiselessall.svg" for dim in suite_info.dimensions
            ],
            goto_dimension=min(
                suite_info.dimensions
            ),  # auto-focus on smallest dimension in html
            rldDimsOfInterest=suite_info.dimensions,
            dimensions_to_display=suite_info.dimensions,
        )
        first_func = min(info.func_id for info in suite_info.function_infos)
        last_func = max(info.func_id for info in suite_info.function_infos)
        fun_settings = dict(
            short_names={info.func_id: info.name for info in suite_info.function_infos},
            first_function_number=first_func,
            last_function_number=last_func,
            functions_with_legend=(first_func, last_func),
        )
        few_targets = [
            10**exp
            for exp in range(suite_info.max_target, suite_info.min_target - 1, -1)
        ]
        many_targets = [
            10**exp
            for exp in np.arange(
                suite_info.max_target, suite_info.min_target - 0.2, -0.2
            )
        ]
        target_settings = dict(
            pptable_ftarget=(
                10**suite_info.min_target
            ),  # value for determining the success ratio in all tables
            ppfvidistr_min_target=10**suite_info.min_target,
            pptable_targetsOfInterest=tuple(few_targets),
            ppfig_target_values=tuple(few_targets),
            pprldistr_target_values=tuple(few_targets),
            pprldmany_target_values=tuple(many_targets),
            hardesttargetlatex=f"$10^{{{suite_info.min_target}}}$",
            pprldmany_target_range_latex=f"$10^{{[{suite_info.min_target}..{suite_info.max_target}]}}$",
        )
        settings = {**suite_settings, **dim_settings, **fun_settings, **target_settings}
        return settings


class TestbedFactory:

    @classmethod
    def create_testbed_class(cls, suite_info: SuiteInfo):
        settings = TestBedSettings(suite_info).settings
        class_name = f"CustomTestbed_{suite_info.name}"

        def __init__(self, target_values):
            for key, val in self.settings.items():
                setattr(self, key, val)
            self.instantiate_attributes(target_values)

        CustomTestbed = type(
            class_name,
            (Testbed,),
            {
                "__init__": __init__,
                "settings": settings,
            },
        )

        # Register the new testbed class in the suite_to_testbed mapping
        suite_to_testbed[suite_info.name] = class_name
        # Inject new class into cocopp namespace so it is available there
        tbs.setattr(tbs, class_name, CustomTestbed)

        return CustomTestbed
