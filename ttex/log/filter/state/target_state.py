import numpy as np

from ttex.log.filter.event.environment_events import EnvironmentStep
from ttex.log.filter.event_keysplit_filter import LogEvent, LoggingState


class TargetState(LoggingState):
    def __init__(
        self, target_key: str, target_val: float | None = None, is_min: bool = True
    ) -> None:
        super().__init__()
        self.target_key = target_key
        self.target_val = target_val
        self.is_min = is_min
        self.best_target: float | None = None  # Best target value observed so from
        self.eval_count = 0  # Count of evaluations processed
        self.best_observed = np.inf if is_min else -np.inf  # Best observed value
        self.best_diff_opt: float | None = (
            None  # Best difference to optimal value (if known)
        )
        self.last_observed: float | None = None  # Last observed value
        self.last_imp: float | None = (
            None  # Improvement of best_observed since last evaluation
        )

    @staticmethod
    def retrieve_val(event: EnvironmentStep, target_key: str) -> float | None:
        val = None
        if target_key.startswith("obs."):
            obs_index = int(target_key[4:])  # Remove "obs." prefix
            val = event.observation.get(obs_index, None)
        elif target_key == "reward":
            val = event.reward
        elif target_key.startswith("info."):
            info_key = target_key[5:]  # Remove "info." prefix
            val = event.info.get(info_key, None)
        else:
            raise ValueError(f"Invalid target_key: {target_key}")
        return val

    @staticmethod
    def get_better(a: float, b: float, is_min: bool) -> float:
        if is_min:
            return min(a, b)
        else:
            return max(a, b)

    @staticmethod
    def get_diff(a: float, b: float, is_min: bool) -> float:
        if is_min:
            return a - b
        else:
            return b - a

    def update(self, event: LogEvent) -> None:
        assert isinstance(
            event, EnvironmentStep
        ), "TargetState can only process EnvironmentStep events"
        val = self.retrieve_val(event, self.target_key)
        assert (
            val is not None
        ), f"Value for target_key '{self.target_key}' not found in event"

        self.eval_count += 1
        self.last_imp = max(self.get_diff(self.best_observed, val, self.is_min), 0)
        self.best_observed = self.get_better(self.best_observed, val, self.is_min)
        self.last_observed = val
        if self.target_val is None:
            self.best_diff_opt = self.best_observed
        else:
            self.best_diff_opt = self.get_diff(
                self.best_observed, self.target_val, self.is_min
            )
