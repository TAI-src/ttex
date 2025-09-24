from dataclasses import dataclass, field


@dataclass
class TestBedSettings:
    name: str
    instances_are_uniform = False
    reference_algorithm_filename = None
    reference_algorithm_displayname = None
    instancesOfInterest = None  # None: consider all instances
    plots_on_main_html_page = []
