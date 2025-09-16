from ttex.log.coco.record import COCOdatRecord, COCOdatHeader
from ..test_coco_events import coco_start_params, eval_params
from ttex.log.coco import COCOState, COCOStart, COCOEval


def test_coco_dat():
    state = COCOState()
    start_event = COCOStart(**coco_start_params)
    state.update(start_event)

    header = COCOdatHeader(state)
    expected_filepath = f"{start_event.algo}/data_{start_event.problem}/{start_event.exp_id}_{start_event.problem}_d{start_event.dim}_i{start_event.inst}.dat"
    assert header.filepath == expected_filepath

    ## dummy initialise
    eval_event = COCOEval(**eval_params)
    state.update(eval_event)
    record = COCOdatRecord(state)

    record.f_evals = 5
    assert record.emit(5)
    record.f_evals = 4
    assert not record.emit(5)
    record.f_evals = 10
    assert record.emit(5)
    record.f_evals = 0
    assert record.emit(5)

    record.f_evals = 1
    assert record.emit(1)
    record.f_evals = 2
    assert record.emit(1)
    record.f_evals = 3
    assert record.emit(1)

    # Test last emit
    state.last_dat_emit = 2
    record.f_evals = 3
    assert not record.emit(2)
    assert record.emit(2, last_dat_emit=state.last_dat_emit)
