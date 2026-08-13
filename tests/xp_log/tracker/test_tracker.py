from ttex.xp_log.tracker.tracker import Tracker
from ttex.xp_log.event.environment_events import EnvironmentStep, EnvironmentReset
import numpy as np


def test_tracker():
    tracker = Tracker(target_key="info.key1.key2")
    initial_info = tracker.get_tracked_info()
    assert initial_info["event_count"] == 0
    assert np.isnan(initial_info["last_observed"])

    event = EnvironmentStep(
        observation=np.array([10, 20, 30]),
        reward=0.0,
        trunc=False,
        term=True,
        info={"key1": {"key2": 42}, "key3": 100, "key4": [1, 2, 3]},
    )
    tracker.process_event(event)
    tracked_info = tracker.get_tracked_info()
    assert tracked_info["event_count"] == 1
    assert tracked_info["last_observed"] == 42

    event2 = EnvironmentStep(
        observation=np.array([40, 50, 60]),
        reward=1.0,
        trunc=False,
        term=False,
        info={"key1": {"key2": 84}, "key3": 200},
    )
    tracker.process_event(event2)
    tracked_info = tracker.get_tracked_info()
    assert tracked_info["event_count"] == 2
    assert tracked_info["last_observed"] == 84


def test_not_log_event():
    tracker = Tracker(target_key="info.key1.key2")
    initial_info = tracker.get_tracked_info()
    assert initial_info["event_count"] == 0
    assert np.isnan(initial_info["last_observed"])

    # Create an event that is not of type LogEvent (e.g., a string)
    non_log_event = "This is not a LogEvent"
    tracker.process_event(non_log_event)

    # The event count and last observed value should remain unchanged
    tracked_info = tracker.get_tracked_info()
    assert tracked_info["event_count"] == 0
    assert np.isnan(tracked_info["last_observed"])


def test_different_event():
    tracker = Tracker(target_key="info.key1.key2", event_type=EnvironmentStep)
    initial_info = tracker.get_tracked_info()
    assert initial_info["event_count"] == 0
    assert np.isnan(initial_info["last_observed"])

    # Create an event of a different type (e.g., EnvironmentReset)
    different_event = EnvironmentReset(
        observation=np.array([0, 0, 0]),
        seed=123,
    )
    tracker.process_event(different_event)

    # The event count and last observed value should remain unchanged
    tracked_info = tracker.get_tracked_info()
    assert tracked_info["event_count"] == 0
    assert np.isnan(tracked_info["last_observed"])
