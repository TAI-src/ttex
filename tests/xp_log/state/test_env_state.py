from ttex.xp_log.state.env_state import (
    SingleEnvironmentState,
    ResetEnvironmentState,
    EnvironmentState,
)
from ttex.xp_log.event.environment_events import (
    EnvironmentClose,
    EnvironmentInit,
    EnvironmentReset,
    EnvironmentStep,
)
from ttex.xp_log.state.config_state import EventIssue
import pytest


def test_single_environment_state():
    exp_id = "test_exp"
    alg_id = "test_alg"
    env_state = SingleEnvironmentState(exp_id=exp_id, alg_id=alg_id)

    # Test initial state
    assert env_state.exp_id == exp_id
    assert env_state.alg_id == alg_id

    # Test valid event
    init_event = EnvironmentInit(exp_id=exp_id, alg_id=alg_id, config={}, kwargs={})
    env_state.update(init_event)
    assert env_state.id == init_event.id

    # Test invalid reset event
    reset_event = EnvironmentReset(exp_id=exp_id, alg_id=alg_id, observation={})
    issues = env_state.validate_event(reset_event)
    assert issues == [EventIssue.INVALID_EVENT_TYPE]
    with pytest.raises(ValueError):
        env_state.update(reset_event)  # Should raise an error due to invalid event type


@pytest.mark.parametrize("with_step", [True, False])
def test_reset_environment_state(with_step):
    exp_id = "test_exp"
    alg_id = "test_alg"
    reset_env_state = ResetEnvironmentState(exp_id=exp_id, alg_id=alg_id)

    # Test initial state
    assert reset_env_state.exp_id == exp_id
    assert reset_env_state.alg_id == alg_id
    assert len(reset_env_state.reset_environments) == 0

    # Test valid init event
    init_event = EnvironmentInit(exp_id=exp_id, alg_id=alg_id, config={}, kwargs={})
    reset_env_state.update(init_event)
    assert reset_env_state.id == init_event.id

    if with_step:
        # Test valid step event
        step_event = EnvironmentStep(
            exp_id=exp_id,
            alg_id=alg_id,
            observation={},
            reward=0.0,
            trunc=False,
            term=False,
            info={},
        )
        reset_env_state.update(step_event)
        assert reset_env_state.event_counter.get(EnvironmentStep.__name__, 0) == 1

    # Test reset event
    reset_event = EnvironmentReset(exp_id=exp_id, alg_id=alg_id, observation={})
    reset_env_state.update(reset_event)
    assert len(reset_env_state.reset_environments) == 1

    assert reset_env_state.reset_environments[-1].id == f"{reset_env_state.id}_reset_0"

    # Test that the new environment state is valid and can accept events
    new_step_event = EnvironmentStep(
        exp_id=exp_id,
        alg_id=alg_id,
        observation={},
        reward=0.0,
        trunc=False,
        term=False,
        info={},
    )
    reset_env_state.update(new_step_event)
    assert (
        reset_env_state.reset_environments[-1].event_counter.get(
            EnvironmentStep.__name__, 0
        )
        == 1
    )

    reset_event_2 = EnvironmentReset(exp_id=exp_id, alg_id=alg_id, observation={})
    reset_env_state.update(reset_event_2)
    assert len(reset_env_state.reset_environments) == 2
    assert reset_env_state.reset_environments[0].closed
    assert not reset_env_state.reset_environments[1].closed
    assert reset_env_state.reset_environments[1].id == f"{reset_env_state.id}_reset_1"

    close_event = EnvironmentClose(exp_id=exp_id, alg_id=alg_id)
    reset_env_state.update(close_event)
    assert reset_env_state.closed
    assert reset_env_state.reset_environments[-1].closed


def test_environment_state_basic():
    exp_id = "test_exp"
    alg_id = "test_alg"
    env_state = EnvironmentState(exp_id=exp_id, alg_id=alg_id)

    # Test valid init event
    init_event = EnvironmentInit(exp_id=exp_id, alg_id=alg_id, config={}, kwargs={})
    env_state.update(init_event)
    assert env_state.id == init_event.id

    # Test valid step event
    step_event = EnvironmentStep(
        exp_id=exp_id,
        alg_id=alg_id,
        observation={},
        reward=0.0,
        trunc=False,
        term=False,
        info={},
    )
    env_state.update(step_event)
    assert env_state.event_counter.get(EnvironmentStep.__name__, 0) == 1

    # reset
    reset_event = EnvironmentReset(exp_id=exp_id, alg_id=alg_id, observation={})
    env_state.update(reset_event)
    assert (
        not env_state.closed
    )  # The environment state should not be closed after a reset

    # Test closing event
    close_event = EnvironmentClose(exp_id=exp_id, alg_id=alg_id)
    env_state.update(close_event)
    assert env_state.closed


def test_nested_environment_states():
    exp_id = "test_exp"
    alg_id = "test_alg"
    env_state = EnvironmentState(exp_id=exp_id, alg_id=alg_id)

    # Initial environment state
    init_event = EnvironmentInit(exp_id=exp_id, alg_id=alg_id, config={}, kwargs={})
    env_state.update(init_event)

    # Nested environment
    nested_init = EnvironmentInit(exp_id=exp_id, alg_id=alg_id, config={}, kwargs={})
    env_state.update(nested_init)
    assert len(env_state.child_environments) == 1

    # Nested environment step
    nested_step = EnvironmentStep(
        exp_id=exp_id,
        alg_id=alg_id,
        observation={},
        reward=0.0,
        trunc=False,
        term=False,
        info={},
    )
    env_state.update(nested_step)
    assert (
        env_state.child_environments[0].event_counter.get(EnvironmentStep.__name__, 0)
        == 1
    )
    assert env_state.event_counter.get(EnvironmentStep.__name__, 0) == 1

    # Close nested environment
    nested_close = EnvironmentClose(exp_id=exp_id, alg_id=alg_id)
    env_state.update(nested_close)
    assert env_state.child_environments[0].closed
    assert not env_state.closed  # The parent environment should not be closed yet

    # new init event
    new_init = EnvironmentInit(exp_id=exp_id, alg_id=alg_id, config={}, kwargs={})
    env_state.update(new_init)
    assert len(env_state.child_environments) == 2
    assert (
        len(env_state.stack) == 1
    )  # The stack should have one active child environment

    # reset the second nested environment
    reset_event = EnvironmentReset(exp_id=exp_id, alg_id=alg_id, observation={})
    env_state.update(reset_event)
    assert len(env_state.reset_environments) == 0
    assert len(env_state.child_environments[1].reset_environments) == 1

    nested_step_2 = EnvironmentStep(
        exp_id=exp_id,
        alg_id=alg_id,
        observation={},
        reward=0.0,
        trunc=False,
        term=False,
        info={},
    )
    env_state.update(nested_step_2)
    assert not env_state.child_environments[1].closed
    assert (
        env_state.child_environments[1].event_counter.get(EnvironmentStep.__name__, 0)
        == 1
    )

    # Close the second nested environment
    nested_close_2 = EnvironmentClose(exp_id=exp_id, alg_id=alg_id)
    env_state.update(nested_close_2)
    assert env_state.child_environments[1].closed
    assert not env_state.closed  # The parent environment should still not be closed

    # Close the parent environment
    parent_close = EnvironmentClose(exp_id=exp_id, alg_id=alg_id)
    env_state.update(parent_close)
    assert env_state.closed  # Now the parent environment should be closed
