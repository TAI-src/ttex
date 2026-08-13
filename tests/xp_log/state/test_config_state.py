from dataclasses import dataclass, field
from uuid import uuid4
from ttex.xp_log.state.config_state import ConfigState, EventIssue
from ttex.xp_log.event.experiment_events import (
    ConfigEvent,
    ExperimentEvent,
    ClosingEvent,
)
from ttex.log.filter.event_keysplit_filter import LogEvent


@dataclass(frozen=True, kw_only=True)
class DummyEvent(LogEvent):
    dummy: str = "test"  # A dummy attribute for testing purposes


@dataclass(frozen=True, kw_only=True)
class DummyConfigEvent(ConfigEvent, ExperimentEvent):
    id: str = field(
        default_factory=lambda: str(uuid4())
    )  # Unique ID for the event, defaults to a random UUID


@dataclass(frozen=True, kw_only=True)
class DummyClosingEvent(ClosingEvent, ExperimentEvent):
    pass


def test_attr_match():
    dummy_event = DummyEvent(dummy="test")
    assert ConfigState.attr_match(dummy_event, "dummy", "test") is True
    assert ConfigState.attr_match(dummy_event, "dummy", "wrong") is False

    dummy_event = DummyEvent()
    assert ConfigState.attr_match(dummy_event, "dummy", "test") is True


def test_validate_event():
    config_state = ConfigState(
        config_event=DummyConfigEvent,
        closing_event=DummyClosingEvent,
        expected_ids={"DummyConfigEvent": "expected_id", "dummy": "expected_dummy"},
    )
    # Test with an invalid event type
    invalid_event = DummyEvent(dummy="invalid")
    issues = config_state.validate_event(invalid_event)
    assert EventIssue.INVALID_EVENT_TYPE in issues
    assert (
        EventIssue.EXPECTED_ID_MISMATCH in issues
    )  # Because the expected ID is not present

    none_id_config = DummyConfigEvent(config={}, kwargs={}, id=None)
    issues = config_state.validate_event(none_id_config)
    assert EventIssue.MISSING_CONFIG_ID in issues  # Because the config event has no ID

    # Test with a valid DummyConfigEvent
    valid_config_event = DummyConfigEvent(config={}, kwargs={})
    issues = config_state.validate_event(valid_config_event)
    assert len(issues) == 0  # No issues should be detected

    # Test with a duplicate DummyConfigEvent
    config_state.config_event = (
        valid_config_event  # Simulate that a config event has been processed
    )
    duplicate_config_event = DummyConfigEvent(config={}, kwargs={})
    issues = config_state.validate_event(duplicate_config_event)
    assert EventIssue.DUPLICATE_CONFIG_EVENT in issues

    # Test wrong id in ExperimentEvent
    experiment_event = ExperimentEvent(id="wrong_id")
    issues = config_state.validate_event(experiment_event)
    assert EventIssue.ID_MISMATCH in issues

    # Test with an ExperimentEvent without a preceding ConfigEvent
    config_state.config_event = None  # Reset to simulate no config event processed
    issues = config_state.validate_event(experiment_event)
    assert EventIssue.MISSING_CONFIG_EVENT in issues

    # Test with a ClosingEvent that has duplicate artifact keys
    config_state.artifacts = {"key1": "value1"}  # Simulate testing
    closing_event = DummyClosingEvent(artifacts={"key1": "value2"})
    issues = config_state.validate_event(closing_event)
    assert EventIssue.DUPLICATE_ARTIFACT_KEY in issues


def test_update():
    config_state = ConfigState(
        config_event=DummyConfigEvent,
        closing_event=DummyClosingEvent,
        expected_ids={"DummyConfigEvent": "expected_id", "dummy": "expected_dummy"},
    )

    # Test updating with a DummyConfigEvent
    config_event = DummyConfigEvent(config={}, kwargs={})
    config_state.update(config_event)
    assert config_state.config_event == config_event
    assert config_state.id == config_event.id  # Check if the ID is set correctly
    assert (
        config_state.last_events["DummyConfigEvent"] == config_event
    )  # Check if the last event is updated

    # Test updating with an ExperimentEvent
    experiment_event = ExperimentEvent(id=config_state.id)
    config_state.update(experiment_event)
    assert (
        config_state.last_events["ExperimentEvent"] == experiment_event
    )  # Check if the last event is updated
    exp_event2 = ExperimentEvent(id=config_state.id)
    config_state.update(exp_event2)
    assert (
        config_state.event_counter["ExperimentEvent"] == 2
    )  # Check if the event counter is updated
    assert (
        config_state.last_events["ExperimentEvent"] == exp_event2
    )  # Check if the last event is updated

    # Test updating with a ClosingEvent
    closing_event = DummyClosingEvent(artifacts={"key1": "value1"})
    config_state.update(closing_event)
    assert config_state.artifacts["key1"] == "value1"  # Check if artifacts are updated
    assert config_state.closed is True  # Check if closed flag is set
