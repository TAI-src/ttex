from ttex.log.filter.tracker.improvement_tracker import ImprovementTracker
from ttex.log.filter.tracker.parser import Parser
from ttex.log.filter.event_keysplit_filter import LogEvent
import numpy as np
from typing import Any


class StepImprovementParser(Parser):
    def __init__(self, step_size: float) -> None:
        super().__init__()
        self.step_size = step_size

    @staticmethod
    def convert_to_step(value: float, step_interval: float = 1e-5) -> float:
        return np.ceil(value / step_interval) * step_interval

    def retrieve_val(self, obj: Any, target_key: str) -> float | None:
        val = super().retrieve_val(obj, target_key)
        if val is not None:
            return StepImprovementParser.convert_to_step(val, self.step_size)
        return None


class StepImprovementTracker(ImprovementTracker):
    def __init__(
        self,
        target_key: str,
        step_size: float,
        is_min: bool = True,
        event_type: type[LogEvent] = LogEvent,
    ) -> None:
        super().__init__(
            target_key=target_key,
            target_val=None,
            is_min=is_min,
            parser=StepImprovementParser(step_size=step_size),
            event_type=event_type,
        )
