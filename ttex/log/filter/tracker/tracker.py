import numpy as np

from ttex.log.filter.event_keysplit_filter import LogEvent
from ttex.log.filter.tracker.parser import Parser


class Tracker:
    def __init__(
        self,
        target_key: str,
        parser: Parser | None = None,
        event_type: type[LogEvent] = LogEvent,
    ) -> None:
        self.parser = parser if parser is not None else Parser()
        self.target_key = target_key
        self.event_type = event_type
        self.event_count = 0  # Count of events processed
        self.last_observed: float = np.nan  # Last observed value

    def _process_event(self, event: LogEvent) -> None:
        pass  # To be implemented by subclasses

    def process_event(self, event: LogEvent) -> None:
        if not isinstance(event, self.event_type):
            return
        self.event_count += 1
        last_observed = self.parser.retrieve_val(event, self.target_key)
        if last_observed is not None:
            self.last_observed = float(last_observed)
        else:
            self.last_observed = np.nan
        assert (
            self.last_observed is not None
        ), f"Value for target_key '{self.target_key}' is None"
        self._process_event(event)

    def get_tracked_info(self) -> dict[str, float]:
        return {
            "event_count": self.event_count,
            "last_observed": self.last_observed,
        }
