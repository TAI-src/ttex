from ttex.log.filter.state.improvement_state import ImprovementState
import numpy as np
from ttex.log.filter.event.environment_events import EnvironmentStep


class StepImprovementState(ImprovementState):
    def __init__(self, target_key: str, step_size: float, is_min: bool = True) -> None:
        super().__init__(target_key, is_min=is_min)
        self.step_size = step_size

    @staticmethod
    def convert_to_step(value: float, step_interval: float = 1e-5) -> float:
        return np.ceil(value / step_interval) * step_interval

    def retrieve_val(self, event: EnvironmentStep, target_key: str) -> float | None:
        val = super().retrieve_val(event, target_key)
        if val is not None:
            return self.convert_to_step(val, self.step_size)
        return None
