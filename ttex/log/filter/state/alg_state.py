from enum import Enum

from ttex.log.filter.event.algorithm_events import (
    AlgorithmEvent,
    AlgorithmStart,
    AlgorithmStop,
    EvaluationEnd,
    EvaluationStart,
    TrainingEnd,
    TrainingStart,
)
from ttex.log.filter.event.environment_events import EnvironmentStep
from ttex.log.filter.event_keysplit_filter import LogEvent
from ttex.log.filter.state.config_state import ConfigState


class Phase(Enum):
    TRAINING = "training"
    EVALUATION = "evaluation"
    IDLE = "idle"


class AlgorithmState(ConfigState):
    def __init__(self, exp_id: str) -> None:
        self.phase = (
            Phase.IDLE
        )  # Current phase of the algorithm (training, evaluation, or idle)
        self.phased_event_counter: dict[Phase, dict[str, int]] = {
            Phase.TRAINING: {},
            Phase.EVALUATION: {},
            Phase.IDLE: {},
        }  # Count of events processed, keyed by phase and event type
        super().__init__(
            config_event=AlgorithmStart,  # The expected configuration event for the algorithm
            closing_event=AlgorithmStop,  # The expected closing event for the algorithm
            expected_ids={"exp_id": exp_id},
            expected_events=[AlgorithmEvent, EnvironmentStep],
            ignored_validation_events=[],
        )  # Initialize the base ConfigState

    def update(self, event: LogEvent) -> None:
        super().update(event)
        if isinstance(event, TrainingStart):
            self.phase = Phase.TRAINING
        elif isinstance(event, TrainingEnd):
            self.phase = Phase.IDLE
        elif isinstance(event, EvaluationStart):
            self.phase = Phase.EVALUATION
        elif isinstance(event, EvaluationEnd):
            self.phase = Phase.IDLE
        else:
            event_type = type(event).__name__
            self.phased_event_counter[self.phase][event_type] = (
                self.phased_event_counter[self.phase].get(event_type, 0) + 1
            )
