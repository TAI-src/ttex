from ttex.log.filter.event_keysplit_filter import LogEvent, LoggingState
from ttex.log.filter.event.experiment_events import (
    EnvironmentStep,
    ExperimentStart,
    ExperimentEnd,
    EnvironmentInit,
    EnvironmentClose,
    EnvironmentReset,
    ExperimentEvent,
    ClosingEvent,
    EnvironmentEvent,
)


class ExperimentState(LoggingState):
    def __init__(self) -> None:
        self.exp_id: str | None = None  # Experiment ID
        self.env_stack: list[str] = []  # Stack of nested environment IDs
        self.artifacts: dict[str, str] = (
            {}
        )  # Dictionary of artifact names to file paths
        self.info: dict[str, str] = {}  # Dictionary of info keys to values
        super().__init__()

    def update(self, event: ExperimentEvent) -> None:
        assert isinstance(event, ExperimentEvent), "Event must be an ExperimentEvent"
        if self.exp_id is not None and event.exp_id is not None:
            assert (
                event.exp_id == self.exp_id
            ), "Event exp_id does not match current ExperimentState exp_id"
        if isinstance(event, ExperimentStart):
            self._update_start(event)
        elif isinstance(event, ExperimentEnd):
            self._update_end(event)
        elif isinstance(event, EnvironmentInit):
            self._update_env_init(event)
        elif isinstance(event, EnvironmentClose):
            self._update_env_close(event)
        elif isinstance(event, EnvironmentStep):
            self._update_env_step(event)
        if isinstance(event, ClosingEvent):
            # TODO: update keys to align with steps
            if event.artifacts is not None:
                self.artifacts.update(event.artifacts)

    def check_id_match(self, event: ExperimentEvent) -> None:
        if self.exp_id is not None and event.exp_id is not None:
            assert (
                event.exp_id == self.exp_id
            ), "Event exp_id does not match current ExperimentState exp_id"
        if (
            isinstance(event, EnvironmentEvent)
            and len(self.env_stack) > 0
            and event.env_id is not None
        ):
            # Check that the env_id matches the current environment or its parent if it's a reset environment
            current_env_id = self.env_stack[-1]
            if self._is_reset_env(current_env_id):
                # If the current environment is a reset environment, we need to check the parent environment
                assert (
                    len(self.env_stack) > 1
                ), "Reset environment must have a parent environment"
                parent_env_id = self.env_stack[-2]
                assert (
                    event.env_id == parent_env_id
                ), "Event env_id does not match parent environment of reset environment"
            else:
                assert (
                    event.env_id == current_env_id
                ), "Event env_id does not match current environment"

    def check_env_state(self, event: EnvironmentEvent) -> bool:
        if isinstance(event, EnvironmentInit):
            assert event.env_id is not None, "EnvironmentInit must have an env_id"
            assert event.env_id not in self.env_steps, "Environment ID already exists"
        else:
            assert len(self.env_stack) > 0, "No environment to operate on"
        return True

    def _update_start(self, exp_start: ExperimentStart) -> None:
        assert exp_start.exp_id is not None, "ExperimentStart must have an exp_id"
        assert self.exp_id is None, "ExperimentState already has an exp_id"
        self.exp_id = exp_start.exp_id
        self.exp_init = exp_start.exp_config

    def _update_end(self, exp_end: ExperimentEnd) -> None:
        assert len(self.env_stack) == 0, "Cannot end experiment with open environments"
        self.exp_id = None

    def _update_env_init(self, env_init: EnvironmentInit) -> None:
        if len(self.env_stack) == 0:
            # This is a new (main) environment, so we start tracking it
            self.env_stack = [
                env_init.env_id
            ]  # Start a new environment stack with the given env_id
            self.env_steps: dict[str, int] = {
                env_init.env_id: 0
            }  # Initialize the step count for the new environment
            self.env_reset: dict[str, int] = {
                env_init.env_id: 0
            }  # Initialize the reset count for the new environment
        else:
            # This is a nested environment, so we add to the env_steps dict
            self.env_steps[env_init.env_id] = 0
            self.env_reset[env_init.env_id] = 0
            self.env_stack.append(env_init.env_id)  # Add the new env_id to the stack

    def _update_env_close(self, env_close: EnvironmentClose) -> str:
        # Pop the current environment from the stack
        closed_env_id = self.env_stack.pop()
        if self._is_reset_env(closed_env_id):
            # If the closed environment is a reset environment, we need to pop the parent as well
            closed_env_id = self.env_stack.pop()
        return closed_env_id

    def _update_env_step(self, env_step: EnvironmentStep) -> None:
        # Increment the step count for all active environments in the stack
        # This allows for nested environments to have their own step count
        for env_id in self.env_stack:
            self.env_steps[env_id] += 1

    def _is_reset_env(self, env_id: str) -> bool:
        # Check if the given env_id is a reset environment
        # A reset environment is one that has a reset counter
        is_reset_env = self.env_reset.get(env_id, None) is not None
        if is_reset_env:
            # If it is a reset environment, check that there is a parent
            assert (
                len(self.env_stack) > 1
            ), "Reset environment must have a parent environment"
        return is_reset_env

    def _update_env_reset(self, env_reset: EnvironmentReset) -> None:
        current_env_id = self.env_stack[-1]
        if self._is_reset_env(current_env_id):
            # Current environment is a reset environment, need to close first
            self.env_stack.pop()  # Close the current reset environment
        # Open a new environment that will act as a reset environment
        new_env_id = f"{current_env_id}_reset_{self.env_reset[current_env_id]}"
        self.env_stack.append(new_env_id)
        self.env_steps[new_env_id] = 0
        # Note: explicitly don't create a reset counter
        self.env_reset[
            current_env_id
        ] += 1  # Increment the reset counter for the current environment
