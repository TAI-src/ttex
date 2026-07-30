from ttex.log.filter.state.experiment_state import ExperimentState
from ttex.log.filter.event.algorithm_events import AlgorithmStart, AlgorithmStop
from ttex.log.filter.event.experiment_events import ExperimentStart, ExperimentEnd
from ttex.log.filter.event.environment_events import EnvironmentInit, EnvironmentClose
from ttex.log.filter.state.run_state import RunState
import pytest


def test_experiment_state_initialization():
    exp_state = ExperimentState()
    assert isinstance(exp_state, ExperimentState)
    assert exp_state.runs == []


def test_basic_experiment_flow():
    exp_state = ExperimentState()

    # Simulate an ExperimentStart event
    exp_start_event = ExperimentStart(id="exp_1", config={}, kwargs={})
    exp_state.update(exp_start_event)
    assert exp_state.config_event == exp_start_event

    # Simulate an AlgorithmStart event to start a run
    alg_start_event = AlgorithmStart(
        exp_id=exp_start_event.id, config={}, kwargs={}, algo_state={}
    )
    exp_state.update(alg_start_event)
    assert len(exp_state.runs) == 1
    assert isinstance(exp_state.runs[0], RunState)

    # Simulate an EnvironmentInit event to start an environment within the run
    env_init_event = EnvironmentInit(config={}, kwargs={})
    exp_state.update(env_init_event)
    assert len(exp_state.runs[0].env_list) == 1

    # Simulate Algorithm End event to close the run
    alg_stop_event = AlgorithmStop(algo_state={})
    exp_state.update(alg_stop_event)
    assert exp_state.runs[0].closed

    # Simulate an EnvironmentClose event to close the environment
    env_close_event = EnvironmentClose(
        exp_id=exp_start_event.id, alg_id=alg_start_event.id
    )
    with pytest.raises(AssertionError):
        exp_state.update(env_close_event)

    # start new run
    alg_start_event_2 = AlgorithmStart(
        exp_id=exp_start_event.id, config={}, kwargs={}, algo_state={}
    )
    exp_state.update(alg_start_event_2)
    assert len(exp_state.runs) == 2

    # Simulate an ExperimentEnd event
    exp_end_event = ExperimentEnd(id="exp_1")
    exp_state.update(exp_end_event)
    assert exp_state.closed
