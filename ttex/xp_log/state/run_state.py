from ttex.log.filter.event_keysplit_filter import LogEvent
from ttex.xp_log.event.algorithm_events import (
    AlgorithmEvent,
    AlgorithmStart,
    AlgorithmStop,
)
from ttex.xp_log.event.environment_events import (
    EnvironmentEvent,
    EnvironmentInit,
    EnvironmentStep,
)
from ttex.xp_log.state.alg_state import AlgorithmState
from ttex.xp_log.state.config_state import ConfigState, EventIssue
from ttex.xp_log.state.env_state import EnvironmentState


class RunState(ConfigState):
    def __init__(self, exp_id: str):
        super().__init__(
            config_event=AlgorithmStart,  # No specific configuration event for the run
            closing_event=AlgorithmStop,  # No specific closing event for the run
            expected_ids={"exp_id": exp_id},
            expected_events=[
                AlgorithmEvent,
                EnvironmentEvent,
            ],  # No specific expected events for the run
            ignored_validation_events=[
                EventIssue.ID_MISMATCH
            ],  # Ignore ID mismatch for the run,
        )
        self.exp_id = exp_id
        self.env_list: list[EnvironmentState] = (
            []
        )  # List to hold EnvironmentState instances for this run
        self.algorithm = AlgorithmState(
            exp_id=exp_id
        )  # Initialize the AlgorithmState for this run

    def update(self, event: LogEvent) -> None:
        super().update(event)
        if isinstance(event, AlgorithmEvent):
            self.algorithm.update(event)
        elif isinstance(event, EnvironmentEvent):
            current_env = self.env_list[-1] if self.env_list else None
            if current_env is None or current_env.closed:
                assert isinstance(
                    event, EnvironmentInit
                ), "The first environment event must be an EnvironmentInit event."
                # Create a new EnvironmentState for the new environment
                assert (
                    self.id is not None
                ), "RunState must have an ID before creating a new environment."
                new_env_state = EnvironmentState(exp_id=self.exp_id, alg_id=self.id)
                self.env_list.append(new_env_state)
                current_env = new_env_state
            current_env.update(event)
        if isinstance(event, EnvironmentStep):
            assert (
                self.algorithm.config_event is not None
            ), "Algorithm configuration event must be set before processing environment steps."
            # Update the algorithm state with the environment step event
            # So it can count the interactions
            self.algorithm.update(event)
