from ttex.xp_log.tracker.improvement_tracker import ImprovementTracker
import numpy as np
from ttex.xp_log.event.environment_events import EnvironmentStep
import pytest


def test_get_better():
    assert ImprovementTracker.get_better(1.0, 2.0, is_min=True) == 1.0
    assert ImprovementTracker.get_better(1.0, 2.0, is_min=False) == 2.0
    # Test with NaN value
    assert ImprovementTracker.get_better(np.nan, 2.0, is_min=True) == 2.0
    assert ImprovementTracker.get_better(1.0, np.nan, is_min=False) == 1.0


def test_get_diff():
    assert ImprovementTracker.get_diff(1.0, 2.0, is_min=True) == -1.0
    assert ImprovementTracker.get_diff(1.0, 2.0, is_min=False) == 1.0

    # Test with NaN value
    assert np.isnan(ImprovementTracker.get_diff(np.nan, 2.0, is_min=True))
    assert np.isnan(ImprovementTracker.get_diff(1.0, np.nan, is_min=False))


def test_init():
    tracker = ImprovementTracker(target_key="obs.0", is_min=True)
    assert tracker.target_key == "obs.0"
    assert tracker.is_min is True
    assert np.isnan(tracker.best_observed)
    assert np.isnan(tracker.best_dist_target)
    assert np.isnan(tracker.last_imp)


@pytest.mark.parametrize("target_val", [None, 0.1])
def test_process_event(target_val):
    tracker = ImprovementTracker(
        target_key="observation.0", is_min=True, target_val=target_val
    )
    event = EnvironmentStep(
        observation=np.array([1.0, 2.0]),
        reward=5.0,
        trunc=False,
        term=False,
        info={"key": 10},
    )
    tracker.process_event(event)
    assert tracker.event_count == 1
    assert tracker.last_observed == 1.0
    assert np.isnan(tracker.last_imp)
    assert tracker.best_observed == 1.0
    assert tracker.last_update == 1
    if target_val is None:
        assert tracker.best_dist_target == 1.0
    else:
        assert tracker.best_dist_target == 0.9  # 1.0 - 0.1

    # Process a better value
    event = EnvironmentStep(
        observation=np.array([0.5, 2.0]),
        reward=5.0,
        trunc=False,
        term=False,
        info={"key": 10},
    )
    tracker.process_event(event)
    assert tracker.event_count == 2
    assert tracker.last_observed == 0.5
    assert tracker.last_imp == 0.5
    assert tracker.best_observed == 0.5
    assert tracker.last_update == 2
    if target_val is None:
        assert tracker.best_dist_target == 0.5
    else:
        assert tracker.best_dist_target == 0.4  # 0.5 - 0.1

    # Process a worse value
    event = EnvironmentStep(
        observation=np.array([1.5, 2.0]),
        reward=5.0,
        trunc=False,
        term=False,
        info={"key": 10},
    )
    tracker.process_event(event)
    assert tracker.event_count == 3
    assert tracker.last_observed == 1.5
    assert tracker.last_imp == 0.0  # No improvement_tracker
    assert tracker.best_observed == 0.5
    assert tracker.last_update == 2  # Last update remains the same
    if target_val is None:
        assert tracker.best_dist_target == 0.5
    else:
        assert tracker.best_dist_target == 0.4  # 0.5 - 0.1
