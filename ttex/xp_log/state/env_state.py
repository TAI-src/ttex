from __future__ import annotations

from copy import deepcopy

from ttex.log.filter.event_keysplit_filter import LogEvent
from ttex.xp_log.event.environment_events import (
    EnvironmentClose,
    EnvironmentEvent,
    EnvironmentInit,
    EnvironmentReset,
    EnvironmentStep,
)
from ttex.xp_log.state.config_state import ConfigState, EventIssue


class SingleEnvironmentState(ConfigState):
    def __init__(self, exp_id: str, alg_id: str, id: str | None = None) -> None:
        super().__init__(
            config_event=EnvironmentInit,
            closing_event=EnvironmentClose,
            expected_ids={"exp_id": exp_id, "alg_id": alg_id},
            expected_events=[EnvironmentEvent],
            ignored_validation_events=[],
            id=id,
        )
        self.exp_id = exp_id
        self.alg_id = alg_id

    def validate_event(self, event: LogEvent) -> list[EventIssue]:
        event_issues = super().validate_event(event)
        if isinstance(event, EnvironmentReset):
            # Reset events are not valid for this environment state, as they indicate a reset of the environment.
            event_issues.append(EventIssue.INVALID_EVENT_TYPE)
        return event_issues


class ResetEnvironmentState(ConfigState):
    def __init__(self, exp_id: str, alg_id: str) -> None:
        super().__init__(
            config_event=EnvironmentInit,
            closing_event=EnvironmentClose,
            expected_ids={"exp_id": exp_id, "alg_id": alg_id},
            expected_events=[EnvironmentEvent],
            ignored_validation_events=[],
        )
        self.reset_environments: list[SingleEnvironmentState] = []
        self.exp_id = exp_id
        self.alg_id = alg_id

    def update(self, event: LogEvent) -> None:
        super().update(event)
        current_env = self.reset_environments[-1] if self.reset_environments else None
        if isinstance(event, EnvironmentReset):
            if current_env is not None:
                # Send closing event to current environment state first
                current_env.update(
                    EnvironmentClose(exp_id=self.exp_id, alg_id=self.alg_id)
                )

            # Create a new EnvironmentState for the reset
            new_env_state = SingleEnvironmentState(
                exp_id=self.exp_id,
                alg_id=self.alg_id,
                id=f"{self.id}_reset_{len(self.reset_environments)}",
            )
            self.reset_environments.append(new_env_state)
            # Send config event to the restarted environment
            assert (
                self.config_event is not None
            ), "Config event must be set before processing reset."

            new_env_state.update(deepcopy(self.config_event))
        elif current_env is not None:
            # Update the current environment state with the event
            current_env.update(event)


class EnvironmentState(ResetEnvironmentState):
    def __init__(self, exp_id: str, alg_id: str) -> None:
        super().__init__(exp_id=exp_id, alg_id=alg_id)
        self.child_environments: list[ResetEnvironmentState] = []
        self.stack: list[int] = (
            []
        )  # Stack to keep track of the current child environment indeces
        self.exp_id = exp_id
        self.alg_id = alg_id

    def update(self, event: LogEvent) -> None:
        if isinstance(event, EnvironmentInit) and self.id is not None:
            # Need to start nested environment
            new_env_state = ResetEnvironmentState(
                exp_id=self.exp_id, alg_id=self.alg_id
            )
            self.child_environments.append(new_env_state)
            self.stack.append(len(self.child_environments) - 1)
            new_env_state.update(event)
        elif isinstance(event, EnvironmentClose) and self.stack:
            # Close the current nested environment
            current_event_id = self.stack.pop()
            current_env = self.child_environments[current_event_id]
            current_env.update(event)
        elif isinstance(event, EnvironmentStep):
            # Update all environments in the stack with the step event
            for env_index in self.stack:
                self.child_environments[env_index].update(event)
            super().update(event)
        elif isinstance(event, EnvironmentReset) and self.stack:
            # Update the current nested environment with the reset event
            current_event_id = self.stack[-1]
            current_env = self.child_environments[current_event_id]
            current_env.update(event)
        else:
            super().update(event)
