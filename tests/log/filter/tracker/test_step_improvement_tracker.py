from ttex.log.filter.tracker.step_improvement_tracker import (
    StepImprovementTracker,
    StepImprovementParser,
)
import math


def test_convert_to_step():
    assert math.isclose(StepImprovementParser.convert_to_step(0.123456, 1), 1.0)
    assert math.isclose(StepImprovementParser.convert_to_step(0.123456, 0.1), 0.2)
    assert math.isclose(StepImprovementParser.convert_to_step(0.123456, 0.01), 0.13)
    assert math.isclose(StepImprovementParser.convert_to_step(0.123456, 0.001), 0.124)
    assert math.isclose(StepImprovementParser.convert_to_step(0.123456, 0.0001), 0.1235)
    assert math.isclose(
        StepImprovementParser.convert_to_step(0.123456, 0.00001), 0.12346
    )


def test_retrieve_val_with_step():
    parser = StepImprovementParser(step_size=0.01)
    obj = {"key": 0.123456}
    assert math.isclose(parser.retrieve_val(obj, "key"), 0.13)

    obj = {"key": 0.1234}
    assert math.isclose(parser.retrieve_val(obj, "key"), 0.13)


def test_retrieve_val_none_with_step():
    parser = StepImprovementParser(step_size=0.01)
    obj = {"key": None}
    assert parser.retrieve_val(obj, "key") is None


def test_step_improvement_tracker_init():
    tracker = StepImprovementTracker(target_key="key", step_size=0.01, is_min=True)
    assert tracker.target_key == "key"
    assert tracker.parser.step_size == 0.01
    assert tracker.is_min is True


def test_step_improvement_tracker_process_event():
    tracker = StepImprovementTracker(
        target_key="key", step_size=0.01, is_min=True, event_type=dict
    )  # Using dict for simplicity in this test
    event = {"key": 0.123456}
    tracker.process_event(event)
    assert tracker.event_count == 1
    assert math.isclose(tracker.last_observed, 0.13)
    assert math.isclose(tracker.best_observed, 0.13)
    assert tracker.last_update == 1

    # Process a better value on same step
    event = {"key": 0.121}
    tracker.process_event(event)
    assert tracker.event_count == 2
    assert math.isclose(tracker.last_observed, 0.13)
    assert math.isclose(
        tracker.best_observed, 0.13
    )  # best should remain 0.13 since it's the same step
    assert tracker.last_update == 1  # last_update should remain 1

    # Process a better value on a new step
    event = {"key": 0.12}
    tracker.process_event(event)
    assert tracker.event_count == 3
    assert math.isclose(tracker.last_observed, 0.12)
    assert math.isclose(tracker.best_observed, 0.12)  # best should update to 0.12
    assert tracker.last_update == 3  # last_update should update to 3

    # Process a worse value
    event = {"key": 0.15}
    tracker.process_event(event)
    assert tracker.event_count == 4
    assert math.isclose(tracker.last_observed, 0.15)
    assert math.isclose(tracker.best_observed, 0.12)  # best should remain 0.12
    assert tracker.last_update == 3  # last_update should remain 3
