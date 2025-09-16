from ttex.log.coco.record import COCOInfoHeader, COCOInfoRecord
from ..test_coco_events import coco_start_params, eval_params, end_params
from ttex.log.coco import COCOState, COCOStart, COCOEval, COCOEnd
import os.path as osp


def test_coco_info():
    state = COCOState()
    start_event = COCOStart(**coco_start_params)
    state.update(start_event)  # Update state with start event

    header = COCOInfoHeader(state)
    ## filepath
    expected_filepath = (
        f"{start_event.algo}/f{start_event.problem}_i{start_event.inst}.info"
    )
    assert header.filepath == expected_filepath
    dummy_dat_filepath = osp.join(
        f"{start_event.algo}/data_f{start_event.problem}", "dummy.dat"
    )
    state.set_dat_filepath(dummy_dat_filepath, header.filepath)

    ## uuid
    expected_uuid = (
        f"{start_event.algo}_{start_event.problem}_{start_event.dim}_{start_event.inst}"
    )
    assert header.uuid == expected_uuid

    expected_header = (
        f"suite = '{state.coco_start.suite}', funcId = {state.coco_start.problem}, DIM = {state.coco_start.dim}, Precision = 1.000e-08, "
        f"algId = '{state.coco_start.algo}', coco_version = '{header.coco_version}', logger = '{header.logger}', "
        f"data_format = '{header.data_format}'\n% {state.coco_start.algo}"
    )
    assert str(header) == expected_header

    evals = 3
    for _ in range(evals):
        eval_event = COCOEval(**eval_params)
        state.update(eval_event)  # Update state with eval event

    end_event = COCOEnd(**end_params)
    state.update(end_event)  # Update state with end event
    record = COCOInfoRecord(state)
    expected_output = (
        f"data_f1/dummy.dat, {start_event.inst}:{evals}|{state.best_dist_opt:.1e}"
    )
    assert str(record) == expected_output


def test_with_alg_info():
    state = COCOState()
    start_params = coco_start_params.copy()
    start_params["algo_info"] = "test info"
    start_event = COCOStart(**start_params)
    state.update(start_event)  # Update state with start event

    header = COCOInfoHeader(state)
    expected_header = (
        f"suite = '{state.coco_start.suite}', funcId = {state.coco_start.problem}, DIM = {state.coco_start.dim}, Precision = 1.000e-08, "
        f"algId = '{state.coco_start.algo}', coco_version = '{header.coco_version}', logger = '{header.logger}', "
        f"data_format = '{header.data_format}'\n% {state.coco_start.algo_info}"
    )
    assert str(header) == expected_header
