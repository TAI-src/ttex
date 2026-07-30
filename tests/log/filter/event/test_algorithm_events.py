from ttex.log.filter.event.algorithm_events import (
    AlgorithmEvent,
    AlgorithmStart,
    TrainingStart,
    TrainingEnd,
    EvaluationStart,
    EvaluationEnd,
    AlgorithmRestart,
    AlgorithmStop,
    AlgorithmAction,
)


def test_algorithm_start():
    algo_state = {"param1": 0.5, "param2": [1, 2, 3]}
    config = {"learning_rate": 0.01}
    kwargs = {"arg1": "valueA", "arg2": 3.14}
    algo_start = AlgorithmStart(
        exp_id="test_exp_id", algo_state=algo_state, config=config, kwargs=kwargs
    )

    assert isinstance(algo_start, AlgorithmEvent)
    assert algo_start.exp_id == "test_exp_id"
    assert algo_start.algo_state == algo_state
    assert algo_start.config == config
    assert algo_start.kwargs == kwargs
    assert isinstance(algo_start.id, str) and len(algo_start.id) > 0


def test_training_events():
    algo_state = {"param1": 0.5, "param2": [1, 2, 3]}
    training_start = TrainingStart(
        exp_id="test_exp_id",
        algo_state=algo_state,
    )
    training_end = TrainingEnd(exp_id="test_exp_id", algo_state=algo_state)

    assert isinstance(training_start, AlgorithmEvent)
    assert isinstance(training_end, AlgorithmEvent)
    assert training_start.exp_id == "test_exp_id"
    assert training_end.exp_id == "test_exp_id"
    assert training_start.algo_state == algo_state
    assert training_end.algo_state == algo_state


def test_evaluation_events():
    algo_state = {"param1": 0.5, "param2": [1, 2, 3]}
    evaluation_start = EvaluationStart(
        exp_id="test_exp_id",
        algo_state=algo_state,
    )
    evaluation_end = EvaluationEnd(exp_id="test_exp_id", algo_state=algo_state)

    assert isinstance(evaluation_start, AlgorithmEvent)
    assert isinstance(evaluation_end, AlgorithmEvent)
    assert evaluation_start.exp_id == "test_exp_id"
    assert evaluation_end.exp_id == "test_exp_id"
    assert evaluation_start.algo_state == algo_state
    assert evaluation_end.algo_state == algo_state


def test_algorithm_event_inheritance():
    algo_state = {"param1": 0.5, "param2": [1, 2, 3]}
    algo_event = AlgorithmEvent(exp_id="test_exp_id", algo_state=algo_state)

    assert isinstance(algo_event, AlgorithmEvent)
    assert algo_event.exp_id == "test_exp_id"
    assert algo_event.algo_state == algo_state


def test_algorithm_restart_and_stop():
    algo_state = {"param1": 0.5, "param2": [1, 2, 3]}
    algo_restart = AlgorithmRestart(exp_id="test_exp_id", algo_state=algo_state)
    algo_stop = AlgorithmStop(exp_id="test_exp_id", algo_state=algo_state)

    assert isinstance(algo_restart, AlgorithmEvent)
    assert isinstance(algo_stop, AlgorithmEvent)
    assert algo_restart.exp_id == "test_exp_id"
    assert algo_stop.exp_id == "test_exp_id"
    assert algo_restart.algo_state == algo_state
    assert algo_stop.algo_state == algo_state


def test_algorithm_action():
    algo_state = {"param1": 0.5, "param2": [1, 2, 3]}
    action = {"move": "forward", "speed": 1.0}
    algo_action = AlgorithmAction(
        exp_id="test_exp_id", algo_state=algo_state, action=action
    )

    assert isinstance(algo_action, AlgorithmEvent)
    assert algo_action.exp_id == "test_exp_id"
    assert algo_action.algo_state == algo_state
    assert algo_action.action == action
