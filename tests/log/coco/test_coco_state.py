from ttex.log.coco import COCOState, COCOStart, COCOEval, COCOEnd
from .test_coco_events import coco_start_params, eval_params, end_params
import pytest
import os.path as osp


def test_coco_state_end():
    state = COCOState()
    assert state._needs_start is True, "State should require a start event"
    with pytest.raises(ValueError):
        state.update(
            "invalid_event"
        )  # Should raise an error for invalid event best_dist_prev

    state._needs_start = False  # Simulate that a start event has been process
    end_event = COCOEnd(**end_params)
    state.update(end_event)
    assert (
        state._needs_start is True
    ), "State should require a start event after COCOEnd"


def test_coco_state_start():
    state = COCOState()
    start_event = COCOStart(**coco_start_params)
    state.update(start_event)

    assert state.f_evals == 0
    assert state.g_evals == 0
    assert state.best_mf == float("inf")
    assert state.fopt == coco_start_params["fopt"]
    assert state.inst == coco_start_params["inst"]
    assert state.coco_start == start_event
    assert state.best_dist_opt is None
    assert state.last_imp is None


def test_ordered_error():
    state = COCOState()
    eval_event = COCOEval(**eval_params)

    # Update state with eval event
    with pytest.raises(
        AssertionError
    ):  # Expect an error since COCOStart must be processed first
        state.update(eval_event)


def test_coco_state_eval():
    state = COCOState()
    start_event = COCOStart(**coco_start_params)
    state.update(start_event)
    eval_event = COCOEval(**eval_params)
    state.update(eval_event)
    assert state.f_evals == 1
    assert state.g_evals == 0
    assert state.best_mf == eval_params["mf"]
    assert state.best_dist_opt == eval_params["mf"] - state.fopt
    assert state.last_imp is not None
    assert state.last_eval == eval_event

    eval2_params = eval_params.copy()
    eval2_params["mf"] = eval_params["mf"] + 0.1  # Simulate a worse evaluation
    eval_event2 = COCOEval(**eval2_params)
    state.update(eval_event2)  # Process the same eval again
    assert state.f_evals == 2
    assert state.g_evals == 0
    assert state.best_mf == eval_params["mf"]
    assert state.last_eval.mf == eval2_params["mf"]
    assert state.best_dist_opt == eval_params["mf"] - state.fopt
    assert state.last_imp == state.best_dist_opt - (eval_params["mf"] - state.fopt)


def test_coco_state_set_dat_filepath():
    state = COCOState()

    dat_filepath = osp.join("root_dir", "dir", "test_dat.txt")
    info_filepath = osp.join("root_dir", "test_info.txt")
    state.set_dat_filepath(dat_filepath, info_filepath)

    expected_path = osp.join("dir", "test_dat.txt")
    assert state.dat_filepath == expected_path
