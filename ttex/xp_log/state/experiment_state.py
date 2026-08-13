from ttex.log.filter.event_keysplit_filter import LogEvent
from ttex.xp_log.event.algorithm_events import AlgorithmStart
from ttex.xp_log.event.experiment_events import (
    ExperimentEnd,
    ExperimentEvent,
    ExperimentStart,
)
from ttex.xp_log.state.config_state import ConfigState
from ttex.xp_log.state.run_state import RunState


class ExperimentState(ConfigState):
    def __init__(self) -> None:
        super().__init__(
            config_event=ExperimentStart,
            closing_event=ExperimentEnd,
            expected_ids={},
            expected_events=[ExperimentEvent],
            ignored_validation_events=[],
        )
        self.runs: list[RunState] = []  # Store the state of each run

    def update(self, event: LogEvent) -> None:
        if isinstance(event, (ExperimentStart, ExperimentEnd)):
            super().update(event)
        else:
            assert (
                self.config_event is not None
            ), "Experiment configuration event must be set before processing run events."
            current_run = self.runs[-1] if self.runs else None
            if current_run is None or current_run.closed:
                assert isinstance(
                    event, AlgorithmStart
                ), "The first run event must be an AlgorithmStart event."
                # Create a new run state for the new run
                assert (
                    self.id is not None
                ), "ExperimentState must have an ID before creating a new run."
                new_run_state = RunState(exp_id=self.id)
                self.runs.append(new_run_state)
                current_run = new_run_state
            assert isinstance(
                current_run, RunState
            ), "Current run state must be an instance of RunState."
            current_run.update(event)
