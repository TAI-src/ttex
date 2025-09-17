from ttex.log.coco.record import COCOdatRecord, COCOdatHeader
from ..test_coco_events import coco_start_params, random_eval_params
from ttex.log.coco import COCOState, COCOStart, COCOEval
import math


def test_ceil_to_target():
    assert math.isclose(COCOdatRecord.ceil_to_target(0.123456, 1), 1.0)
    assert math.isclose(COCOdatRecord.ceil_to_target(0.123456, 0.1), 0.2)
    assert math.isclose(COCOdatRecord.ceil_to_target(0.123456, 0.01), 0.13)
    assert math.isclose(COCOdatRecord.ceil_to_target(0.123456, 0.001), 0.124)
    assert math.isclose(COCOdatRecord.ceil_to_target(0.123456, 0.0001), 0.1235)
    assert math.isclose(COCOdatRecord.ceil_to_target(0.123456, 0.00001), 0.12346)


def test_improvement_trigger():
    state = COCOState()
    start_event = COCOStart(**coco_start_params)
    state.update(start_event)

    ## dummy initialise
    eval_event = COCOEval(**random_eval_params(dim=coco_start_params["dim"]))
    state.update(eval_event)
    record = COCOdatRecord(state)

    precision = 0.1
    record.mf = 0.25  # prev best mf = 0.3, so last target reached = 0.3
    record.last_imp = 0.05
    assert not record.improvement_trigger(
        precision
    )  # new target reached = 0.3, so no new target
    record.mf = 0.2  # prev best mf = 0.3, so last target reached = 0.3
    record.last_imp = 0.05
    assert record.improvement_trigger(
        precision
    )  # new target reached = 0.2, so new target
    record.mf = 0.15  # prev best mf = 0.2 (mf+last_imp), so last target reached = 0.2
    record.last_imp = 0.05
    assert not record.improvement_trigger(
        precision
    )  # new target reached = 0.2, so no new target


def test_log_target_trigger():
    state = COCOState()
    start_event = COCOStart(**coco_start_params)
    state.update(start_event)

    ## dummy initialise
    eval_event = COCOEval(**random_eval_params(dim=coco_start_params["dim"]))
    state.update(eval_event)
    record = COCOdatRecord(state)

    n_triggers = 10
    record.best_dist_opt = 1.0
    record.last_imp = 0.2  # so prev best_dist_opt = 1.2, prev target = 1.2589
    assert record.log_target_trigger(n_triggers)

    record.best_dist_opt = 9
    record.last_imp = 1  # so prev best_dist_opt = 10, prev target = 10
    assert not record.log_target_trigger(n_triggers)

    # Check we stop logging when within precision of optimum
    record.best_dist_opt = 1e-9
    record.last_imp = 1
    assert not record.log_target_trigger(n_triggers, target_precision=1e-8)


def test_emit():
    state = COCOState()
    start_event = COCOStart(**coco_start_params)
    state.update(start_event)

    ## dummy initialise
    eval_event = COCOEval(**random_eval_params(dim=coco_start_params["dim"]))
    state.update(eval_event)
    record = COCOdatRecord(state)

    # No triggers set, should not emit
    record.f_evals = 2  # to avoid first eval auto-emit
    assert not record.emit(improvement_step=0, number_target_triggers=0)

    # Improvement trigger only
    precision = 0.1
    record.mf = 0.25  # prev best mf = 0.3, so last target reached = 0.3
    record.last_imp = 0.05
    assert not record.emit(
        improvement_step=precision, number_target_triggers=0
    )  # no new target
    record.mf = 0.2  # prev best mf = 0.3, so last target reached = 0.3
    record.last_imp = 0.05
    assert record.emit(
        improvement_step=precision, number_target_triggers=0
    )  # new target

    # Target triggers only
    n_triggers = 10
    record.best_dist_opt = 1.0
    record.last_imp = 0.2  # so prev best_dist_opt = 1.2, prev target = 1.2589
    assert record.emit(
        improvement_step=0, number_target_triggers=n_triggers, target_precision=1e-8
    )
    record.best_dist_opt = 9
    record.last_imp = 1  # so prev best_dist_opt = 10, prev target = 10
    assert not record.emit(
        improvement_step=0, number_target_triggers=n_triggers, target_precision=1e-8
    )
