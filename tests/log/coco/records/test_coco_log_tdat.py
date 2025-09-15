from ttex.log.coco.record import COCOtdatRecord, COCOtdatHeader
from ..test_coco_events import coco_start_params, eval_params
from ttex.log.coco import COCOState, COCOStart, COCOEval


def test_coco_dat():
    state = COCOState()
    start_event = COCOStart(**coco_start_params)
    state.update(start_event)

    header = COCOtdatHeader(state)
    expected_filepath = f"{start_event.algo}/data_{start_event.problem}/{start_event.exp_id}_{start_event.problem}_d{start_event.dim}_i{start_event.inst}.tdat"
    assert header.filepath == expected_filepath

    ## dummy initialise
    eval_event = COCOEval(**eval_params)
    state.update(eval_event)
    record = COCOtdatRecord(state)

    trigger_targers = [0.1, 0.05]
    record.best_dist_opt = 0.1
    assert record.emit(trigger_targers)
    assert trigger_targers == [0.05]  # popped and changed the list
    record.best_dist_opt = 0.09
    assert not record.emit(trigger_targers)
    record.best_dist_opt = 0.05
    assert record.emit(trigger_targers)
    assert trigger_targers == []  # popped and changed the list
    record.best_dist_opt = 0.04
    assert not record.emit(trigger_targers)
    record.best_dist_opt = 0.03
    assert not record.emit(trigger_targers)
