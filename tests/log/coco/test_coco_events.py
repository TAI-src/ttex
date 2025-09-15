from ttex.log.coco import COCOEval, COCOEnd, COCOStart
from ttex.log.filter import LogEvent
import pytest
from dataclasses import FrozenInstanceError

coco_start_params = {
    "fopt": 0.1,
    "algo": "test_algo",
    "problem": 1,
    "dim": 10,
    "inst": 1,
    "suite": "test_suite",
    "exp_id": "test_exp_id",
}

eval_params = {
    "x": [1.0, 2.0, 3.0],
    "mf": 0.5,
}

end_params = {}


def test_coco_start():
    event = COCOStart(**coco_start_params)
    assert isinstance(event, LogEvent)
    assert event.fopt == 0.1
    assert event.algo == "test_algo"
    assert event.problem == 1
    assert event.dim == 10
    assert event.inst == 1
    assert event.suite == "test_suite"
    assert isinstance(event.exp_id, str)

    with pytest.raises(FrozenInstanceError):
        # Attempting to modify a frozen dataclass should raise an error
        event.exp_id = "custom_id"


def test_coco_start_custom_exp_id():
    custom_exp_id = "custom_id"
    start_params = coco_start_params.copy()
    start_params["exp_id"] = custom_exp_id
    event = COCOStart(**start_params)
    assert event.exp_id == custom_exp_id


def test_coco_eval():
    event = COCOEval(**eval_params)
    assert isinstance(event, LogEvent)
    assert event.x == [1.0, 2.0, 3.0]
    assert event.mf == 0.5


def test_coco_end():
    event = COCOEnd(**end_params)
    assert isinstance(event, LogEvent)

    # COCOEnd has no attributes, so we just check that it can be instantiated
    assert event is not None
