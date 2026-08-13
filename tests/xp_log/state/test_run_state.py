from ttex.xp_log.event.algorithm_events import (
    TrainingStart,
    AlgorithmStart,
    TrainingEnd,
    EvaluationStart,
    EvaluationEnd,
    AlgorithmStop,
)
from ttex.xp_log.state.run_state import RunState
from ttex.xp_log.state.alg_state import AlgorithmState, Phase
from ttex.xp_log.event.environment_events import (
    EnvironmentClose,
    EnvironmentInit,
    EnvironmentStep,
)
import pytest


def test_run_state_initialization():
    exp_id = "test_exp"
    run_state = RunState(exp_id=exp_id)

    assert run_state.exp_id == exp_id
    assert isinstance(run_state.algorithm, AlgorithmState)
    assert run_state.env_list == []


def test_validate_event_with_missing_config():
    exp_id = "test_exp"
    run_state = RunState(exp_id=exp_id)

    env_init = EnvironmentInit(
        id="env_init_1", exp_id=exp_id, alg_id="alg_1", config={}, kwargs={}
    )
    with pytest.raises(ValueError):
        run_state.update(
            env_init
        )  # Should raise an error due to missing algorithm config event


def test_basic():
    exp_id = "test_exp"
    run_state = RunState(exp_id=exp_id)

    # Simulate an AlgorithmStart event
    alg_start_event = AlgorithmStart(exp_id=exp_id, config={}, kwargs={}, algo_state={})
    run_state.update(alg_start_event)

    # start training
    training_event = TrainingStart(exp_id=exp_id, algo_state={})

    run_state.update(training_event)

    # Now simulate an EnvironmentInit event
    env_init_event = EnvironmentInit(
        exp_id=exp_id, alg_id=alg_start_event.id, config={}, kwargs={}
    )
    run_state.update(env_init_event)

    # Check that the environment state was created and added to the list
    assert len(run_state.env_list) == 1
    assert run_state.env_list[0].id == env_init_event.id

    # step environment
    env_step_event = EnvironmentStep(
        observation={},
        reward=0.0,
        trunc=False,
        term=False,
        info={},
    )
    run_state.update(env_step_event)

    # close environment
    close_env_event = EnvironmentClose()
    run_state.update(close_env_event)

    # Start evaluation phase
    training_stop = TrainingEnd(exp_id=exp_id, algo_state={})
    run_state.update(training_stop)
    eval_start = EvaluationStart(exp_id=exp_id, algo_state={})
    run_state.update(eval_start)

    # start enviornment for evaluation
    env_init_event_eval = EnvironmentInit(
        exp_id=exp_id, alg_id=alg_start_event.id, config={}, kwargs={}
    )
    run_state.update(env_init_event_eval)

    env_step = EnvironmentStep(
        observation={},
        reward=0.0,
        trunc=False,
        term=False,
        info={},
    )
    run_state.update(env_step)

    # close environment for evaluation
    close_env_event_eval = EnvironmentClose()
    run_state.update(close_env_event_eval)

    # start another environment for evaluation
    env_init_event_eval_2 = EnvironmentInit(
        exp_id=exp_id, alg_id=alg_start_event.id, config={}, kwargs={}
    )
    run_state.update(env_init_event_eval_2)
    run_state.update(env_step)
    run_state.update(env_step)  # Two steps in the second evaluation environment

    # stop evaluation phase
    eval_stop = EvaluationEnd(exp_id=exp_id, algo_state={})
    run_state.update(eval_stop)

    # stop algorithm
    alg_stop_event = AlgorithmStop(exp_id=exp_id, algo_state={})
    run_state.update(alg_stop_event)

    assert run_state.closed
    assert len(run_state.env_list) == 3

    p_event_counter = run_state.algorithm.phased_event_counter
    assert p_event_counter[Phase.TRAINING]["EnvironmentStep"] == 1
    assert p_event_counter[Phase.EVALUATION]["EnvironmentStep"] == 3
