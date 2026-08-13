from collections import defaultdict
from copy import deepcopy
from enum import Enum
from typing import Any

from ttex.log.filter.event_keysplit_filter import LogEvent, LoggingState
from ttex.xp_log.event.experiment_events import (
    ClosingEvent,
    ConfigEvent,
    ExperimentEvent,
)


class EventIssue(Enum):
    DUPLICATE_CONFIG_EVENT = "Duplicate ConfigEvent detected"
    MISSING_CONFIG_EVENT = "Missing ConfigEvent before ExperimentEvent"
    ID_MISMATCH = "ID does not match ConfigEvent ID"
    EXPECTED_ID_MISMATCH = "ExperimentEvent expected ID does not match"
    EVENT_AFTER_CLOSED = "Cannot process events after a ClosingEvent has been observed"
    INVALID_EVENT_TYPE = "Invalid event type for ConfigState"
    DUPLICATE_ARTIFACT_KEY = "Duplicate artifact key detected in ClosingEvent"
    MISSING_CONFIG_ID = "ConfigEvent is missing an ID, which is required for validation"


class ConfigState(LoggingState):
    def __init__(
        self,
        config_event: type[ConfigEvent],
        closing_event: type[ClosingEvent],
        expected_ids: dict | None = None,
        ignored_validation_events: list[EventIssue] | None = None,
        expected_events: list[type[ExperimentEvent]] | None = None,
        id: str | None = None,
    ) -> None:
        self.config_event_type = config_event
        self.config_event: ConfigEvent | None = None
        self.closing_event_type = closing_event
        self.last_events: dict[str, ExperimentEvent] = (
            {}
        )  # Store the last event of each type
        self.expected_ids = expected_ids if expected_ids is not None else {}
        self.artifacts: dict[str, str] = {}  # Store artifacts from ClosingEvent
        self.event_counter: dict[str, int] = defaultdict(
            int
        )  # Count of events processed, keyed by event type
        self.closed = False  # Flag to indicate if a closing event has been observed
        self.ignored_validation_events = (
            ignored_validation_events if ignored_validation_events is not None else []
        )
        self.expected_events = expected_events if expected_events is not None else []
        self.id = id  # Optional ID for the ConfigState instance

    @staticmethod
    def attr_match(obj: Any, attr_name: str, expected_value: Any) -> bool:
        val = getattr(obj, attr_name, None)
        if val is None:
            return True  # If the attribute is not present, we consider it a match
        return val == expected_value

    def validate_event(self, event: LogEvent) -> list[EventIssue]:
        detected_issues = []
        expected_event = (
            any(
                isinstance(event, expected_type)
                for expected_type in self.expected_events
            )
            or len(self.expected_events) == 0
        )
        if not expected_event:
            detected_issues.append(EventIssue.INVALID_EVENT_TYPE)
        if isinstance(event, self.config_event_type):
            if self.config_event is not None:
                detected_issues.append(EventIssue.DUPLICATE_CONFIG_EVENT)
            if getattr(event, "id", None) is None:
                detected_issues.append(EventIssue.MISSING_CONFIG_ID)
        elif isinstance(event, ExperimentEvent):
            if self.closed:
                detected_issues.append(EventIssue.EVENT_AFTER_CLOSED)
            if self.config_event is None:
                detected_issues.append(EventIssue.MISSING_CONFIG_EVENT)
            elif not self.attr_match(event, "id", self.id):
                detected_issues.append(EventIssue.ID_MISMATCH)
        else:
            detected_issues.append(EventIssue.INVALID_EVENT_TYPE)

        for exp_id, exp_val in self.expected_ids.items():
            if not self.attr_match(event, exp_id, exp_val):
                detected_issues.append(EventIssue.EXPECTED_ID_MISMATCH)

        if isinstance(event, ClosingEvent):
            # check that no keys of artifacts are being overwritten
            for key in event.artifacts or {}:
                if key in self.artifacts:
                    detected_issues.append(EventIssue.DUPLICATE_ARTIFACT_KEY)
                    break  # No need to check further if a duplicate is found
        return detected_issues

    def update(self, event: LogEvent) -> None:
        validation_issues = self.validate_event(event)
        # Filter out ignored validation issues
        validation_issues = [
            issue
            for issue in validation_issues
            if issue not in self.ignored_validation_events
        ]
        if len(validation_issues) > 0:
            raise ValueError(
                f"Validation issues detected for event {type(event).__name__}: {[issue.value for issue in validation_issues]}"
            )
        assert isinstance(
            event, ExperimentEvent
        ), "Event must be an instance of ExperimentEvent"

        event_type = type(event).__name__
        self.event_counter[event_type] = self.event_counter.get(event_type, 0) + 1
        event_copy = deepcopy(event)
        self.last_events[event_type] = event_copy
        if isinstance(event, self.config_event_type):
            assert isinstance(event_copy, ConfigEvent)
            self.config_event = event_copy
            self.id = self.id or event_copy.id  # Set the ID if not already set

        if isinstance(event, ClosingEvent):
            self.artifacts.update(event.artifacts or {})
            if isinstance(event, self.closing_event_type):
                self.closed = True

    def to_dict(self) -> dict:
        return {
            "artifacts": self.artifacts,
            "event_counter": self.event_counter,
        }
