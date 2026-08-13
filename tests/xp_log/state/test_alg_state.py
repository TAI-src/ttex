from ttex.xp_log.state.alg_state import AlgorithmState, Phase
from ttex.xp_log.event.algorithm_events import (
    AlgorithmStart,
    AlgorithmStop,
    TrainingStart,
    TrainingEnd,
    EvaluationStart,
    EvaluationEnd,
    AlgorithmEvent,
)
from ttex.xp_log.event.environment_events import EnvironmentStep
import pytest


def test_init():
    exp_id = "test_exp"
    alg_state = AlgorithmState(exp_id=exp_id)
    assert alg_state.phase == Phase.IDLE
    assert alg_state.phased_event_counter == {
        Phase.TRAINING: {},
        Phase.EVALUATION: {},
        Phase.IDLE: {},
    }
    assert alg_state.expected_ids == {"exp_id": exp_id}
    assert alg_state.config_event_type == AlgorithmStart
    assert alg_state.closing_event_type == AlgorithmStop
    assert alg_state.expected_events == [AlgorithmEvent, EnvironmentStep]


def test_phase_transitions():
    exp_id = "test_exp"
    alg_state = AlgorithmState(exp_id=exp_id)

    with pytest.raises(ValueError):
        alg_state.update(
            TrainingStart(exp_id=exp_id, algo_state={})
        )  # Should raise an error because AlgorithmStart hasn't been processed pytest

    # start algorithm
    alg_state.update(AlgorithmStart(exp_id=exp_id, algo_state={}, config={}, kwargs={}))
    assert alg_state.phase == Phase.IDLE

    # Transition to TRAINING phase
    alg_state.update(TrainingStart(exp_id=exp_id, algo_state={}))
    assert alg_state.phase == Phase.TRAINING

    # Transition back to IDLE phase
    alg_state.update(TrainingEnd(exp_id=exp_id, algo_state={}))
    assert alg_state.phase == Phase.IDLE

    # Transition to EVALUATION phase
    alg_state.update(EvaluationStart(exp_id=exp_id, algo_state={}))
    assert alg_state.phase == Phase.EVALUATION

    # Transition back to IDLE phase
    alg_state.update(EvaluationEnd(exp_id=exp_id, algo_state={}))
    assert alg_state.phase == Phase.IDLE


def test_event_counting():
    exp_id = "test_exp"
    alg_state = AlgorithmState(exp_id=exp_id)

    # Start the algorithm
    alg_state.update(AlgorithmStart(exp_id=exp_id, algo_state={}, config={}, kwargs={}))

    # Transition to TRAINING phase and send events
    alg_state.update(TrainingStart(exp_id=exp_id, algo_state={}))
    alg_state.update(
        EnvironmentStep(
            exp_id=exp_id,
            observation={},
            reward=0.0,
            trunc=False,
            term=False,
            info={},
        )
    )
    alg_state.update(
        EnvironmentStep(
            observation={},
            reward=0.0,
            trunc=False,
            term=False,
            info={},
        )
    )
    assert alg_state.phased_event_counter[Phase.TRAINING] == {"EnvironmentStep": 2}

    # Transition to EVALUATION phase and send events
    alg_state.update(TrainingEnd(exp_id=exp_id, algo_state={}))
    alg_state.update(EvaluationStart(exp_id=exp_id, algo_state={}))
    alg_state.update(
        EnvironmentStep(
            exp_id=exp_id, observation={}, reward=0.0, trunc=False, term=False, info={}
        )
    )
    assert alg_state.phased_event_counter[Phase.EVALUATION] == {"EnvironmentStep": 1}

    assert alg_state.event_counter["AlgorithmStart"] == 1
    assert alg_state.event_counter["TrainingStart"] == 1
    assert alg_state.event_counter["TrainingEnd"] == 1
    assert alg_state.event_counter["EnvironmentStep"] == 3
