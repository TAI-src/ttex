from ttex.log.filter.state.target_state import ImprovementState
from ttex.log.filter.event.environment_events import EnvironmentStep
import numpy as np
import pytest


def test_retrieve_val():
    # Test retrieving observation value
    event = EnvironmentStep(
        observation=np.array([1.0, 2.0]),
        reward=5.0,
        trunc=False,
        term=False,
        info={"key": 10},
    )
    assert ImprovementState.retrieve_val(event, "obs.0") == 1.0
    assert ImprovementState.retrieve_val(event, "obs.1") == 2.0

    # Test retrieving reward value
    assert ImprovementState.retrieve_val(event, "reward") == 5.0

    # Test retrieving info value
    assert ImprovementState.retrieve_val(event, "info.key") == 10

    # Test invalid target_key
    try:
        ImprovementState.retrieve_val(event, "invalid.key")
        assert False, "Expected ValueError for invalid target_key"
    except ValueError:
        pass

    # Test observation index out of bounds
    try:
        ImprovementState.retrieve_val(event, "obs.2")
        assert False, "Expected AssertionError for observation index out of bounds"
    except AssertionError:
        pass

    # Test negative observation index
    try:
        ImprovementState.retrieve_val(event, "obs.-1")
        assert False, "Expected AssertionError for negative observation index"
    except AssertionError:
        pass

    # Test non-integer observation index
    try:
        ImprovementState.retrieve_val(event, "obs.invalid")
        assert False, "Expected ValueError for non-integer observation index"
    except AssertionError:
        pass

    # Test observation key that is not an integer
    event = EnvironmentStep(
        observation={"key": 3.0},
        reward=5.0,
        trunc=False,
        term=False,
        info={"key": 10},
    )
    assert ImprovementState.retrieve_val(event, "obs.key") == 3.0


def test_get_better():
    assert ImprovementState.get_better(1.0, 2.0, is_min=True) == 1.0
    assert ImprovementState.get_better(1.0, 2.0, is_min=False) == 2.0
    # Test with NaN value
    assert ImprovementState.get_better(np.nan, 2.0, is_min=True) == 2.0
    assert ImprovementState.get_better(1.0, np.nan, is_min=False) == 1.0


def test_get_diff():
    assert ImprovementState.get_diff(1.0, 2.0, is_min=True) == -1.0
    assert ImprovementState.get_diff(1.0, 2.0, is_min=False) == 1.0

    # Test with NaN value
    assert np.isnan(ImprovementState.get_diff(np.nan, 2.0, is_min=True))
    assert np.isnan(ImprovementState.get_diff(1.0, np.nan, is_min=False))


def test_init():
    target_state = ImprovementState(target_key="obs.0", is_min=True)
    assert target_state.target_key == "obs.0"
    assert target_state.is_min is True
    assert target_state.eval_count == 0
    assert np.isnan(target_state.best_observed)
    assert np.isnan(target_state.last_observed)
    assert np.isnan(target_state.last_imp)
    assert np.isnan(target_state.best_diff_opt)


@pytest.mark.parametrize("target_val", [None, 0.1])
def test_update(target_val):
    target_state = ImprovementState(
        target_key="obs.0", is_min=True, target_val=target_val
    )
    event = EnvironmentStep(
        observation=np.array([1.0, 2.0]),
        reward=5.0,
        trunc=False,
        term=False,
        info={"key": 10},
    )
    target_state.update(event)
    assert target_state.eval_count == 1
    assert target_state.best_observed == 1.0
    assert target_state.last_observed == 1.0
    assert np.isnan(target_state.last_imp)
    if target_val is None:
        assert target_state.best_diff_opt == 1.0
    else:
        assert target_state.best_diff_opt == 0.9  # 1.0 - 0.1

    # Update with a better value
    event = EnvironmentStep(
        observation=np.array([0.5, 2.0]),
        reward=5.0,
        trunc=False,
        term=False,
        info={"key": 10},
    )
    target_state.update(event)
    assert target_state.eval_count == 2
    assert target_state.best_observed == 0.5
    assert target_state.last_observed == 0.5
    assert target_state.last_imp == 0.5
    if target_val is None:
        assert target_state.best_diff_opt == 0.5
    else:
        assert target_state.best_diff_opt == 0.4  # 0.5 - 0.1

    # Update with a worse value
    event = EnvironmentStep(
        observation=np.array([1.5, 2.0]),
        reward=5.0,
        trunc=False,
        term=False,
        info={"key": 10},
    )
    target_state.update(event)
    assert target_state.eval_count == 3
    assert target_state.best_observed == 0.5
    assert target_state.last_observed == 1.5
    assert target_state.last_imp == 0
    if target_val is None:
        assert target_state.best_diff_opt == 0.5
    else:
        assert target_state.best_diff_opt == 0.4  # 0.5 - 0.1
