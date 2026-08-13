import numpy as np

from ttex.log.filter.event_keysplit_filter import LogEvent
from ttex.log.filter.tracker.parser import Parser
from ttex.log.filter.tracker.tracker import Tracker


class ImprovementTracker(Tracker):
    def __init__(
        self,
        target_key: str,
        target_val: float | None = None,
        is_min: bool = True,
        parser: Parser | None = None,
        event_type: type[LogEvent] = LogEvent,
    ) -> None:
        super().__init__(target_key=target_key, parser=parser, event_type=event_type)
        self.target_val = target_val
        self.is_min = is_min
        self.best_observed: float = np.nan  # Best observed value
        self.best_dist_target: float = (
            np.nan
        )  # Best difference to optimal value (if known)
        self.last_imp: float = (
            np.nan
        )  # Improvement of best_observed since last evaluation
        self.last_update: int = 1  # Last event count when best_observed was updated

    @staticmethod
    def get_better(a: float, b: float, is_min: bool) -> float:
        if is_min:
            return np.nanmin([a, b])
        else:
            return np.nanmax([a, b])

    @staticmethod
    def get_diff(a: float, b: float, is_min: bool) -> float:
        if is_min:
            return a - b
        else:
            return b - a

    def _process_event(self, event: LogEvent) -> None:
        val = self.last_observed
        self.last_imp = np.maximum(
            self.get_diff(self.best_observed, val, self.is_min), 0
        )
        if self.last_imp > 0:
            self.last_update = self.event_count
        self.best_observed = self.get_better(self.best_observed, val, self.is_min)
        if self.target_val is None:
            self.best_dist_target = self.best_observed
        else:
            self.best_dist_target = self.get_diff(
                self.best_observed, self.target_val, self.is_min
            )

    def get_tracked_info(self) -> dict[str, float]:
        info = super().get_tracked_info()
        info.update(
            {
                "best_observed": self.best_observed,
                "best_dist_target": self.best_dist_target,
                "last_imp": self.last_imp,
                "last_update": self.last_update,
            }
        )
        return info
