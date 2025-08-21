from ttex.log.filter import COCOLoggerFilter as COCOFilter
from logging import makeLogRecord
import pytest
from ttex.log.record import COCOStart, COCOEval, COCOEnd
import os.path as osp


def test_trigger_nth_eval():
    """
    Test the trigger_nth_eval method of COCOFilter.
    """
    filter = COCOFilter(trigger_nth=5)
    assert filter.trigger_nth_eval(5) is True
    assert filter.trigger_nth_eval(4) is False
    assert filter.trigger_nth_eval(10) is True
    assert filter.trigger_nth_eval(0) is True

    filter = COCOFilter(trigger_nth=1)
    assert filter.trigger_nth_eval(1) is True
    assert filter.trigger_nth_eval(2) is True
    assert filter.trigger_nth_eval(3) is True


def test_trigger_imp_eval():
    """
    Test the trigger_imp_eval method of COCOFilter.
    """
    filter = COCOFilter(trigger_imp=0.1)
    assert filter.trigger_imp_eval(0.1) is True
    assert filter.trigger_imp_eval(0.05) is False
    assert filter.trigger_imp_eval(0.2) is True
    assert filter.trigger_imp_eval(0) is False


def test_trigger_target_eval():
    """
    Test the trigger_target_eval method of COCOFilter.
    """
    filter = COCOFilter(trigger_targets=[0.05, 0.1])
    assert filter.trigger_target_eval(0.1) is True
    assert filter.trigger_target_eval(0.09) is False
    assert filter.trigger_target_eval(0.05) is True
    assert filter.trigger_target_eval(0.04) is False
    assert filter.trigger_target_eval(0.03) is False  # No more targets left


def test_trigger_emit():
    """
    Test the combined triggers of COCOFilter.
    """
    filter = COCOFilter(trigger_nth=5, trigger_imp=0.1, trigger_targets=[0.05])

    assert filter.trigger_emit(0.1, 5, 0.1) is True  # nth eval and imp trigger
    assert filter.trigger_emit(0.05, 4, 0.1) is False  # No triggers
    assert filter.trigger_emit(0.1, 10, 0.04) is True  # nth eval trigger
    assert filter.trigger_emit(0.1, 3, 0.05) is True  # imp and target trigger


def test_filter_not_coco():
    """
    Test that COCOFilter only allows COCOHeader and COCORecord.
    """
    filter = COCOFilter()

    record = makeLogRecord({"msg": "Not a COCO record"})
    assert not filter.filter(record), "Non-COCO record should be filtered out"


start_vals = {
    "fopt": 7.0,
    "algo": "test_algo",
    "problem": 1,
    "dim": 2,
    "inst": 3,
    "exp_id": "1234",
    "suite": "test_suite",
}


def test_coco_start():
    filter = COCOFilter()
    assert filter.log_filepath is None, "Initial log filter should be None"
    filter.f_evals = 5  # Set some initial evaluations

    record = COCOStart(**start_vals)
    log_record = makeLogRecord({"msg": record})
    assert filter.filter(log_record), "COCOStart should be allowed"
    assert filter.f_evals == 0, "Function evaluations should be reset to 0"
    assert filter.g_evals == 0, "Gradient evaluations should be reset to 0"
    assert filter.best_mf == float(
        "inf"
    ), "Best measured fitness should be initialized to infinity"
    assert filter.inst == record.inst, "Instance should match the record instance"
    assert filter.f_opt == record.fopt, "f_opt should be set from COCOStart"

    assert hasattr(log_record, "info"), "COCOStart should attach info record"
    assert hasattr(log_record, "log"), "COCOStart should attach log record"
    assert filter.log_filepath == osp.join(
        f"data_{record.problem}", f"{record.exp_id}_{record.problem}_d{record.dim}.dat"
    ), "Log filepath should match expected format"

    assert log_record.info.suite == record.suite, "Suite should match"
    assert log_record.info.funcId == record.problem, "Problem ID should match"
    assert log_record.info.dim == record.dim, "Dimension should match"
    assert log_record.info.algId == record.algo, "Algorithm ID should match"
    assert log_record.log.fopt == record.fopt, "fopt should match"
    assert (
        log_record.log.uuid
        == f"{record.algo}_{record.problem}_d{record.dim}_i{record.inst}_{record.exp_id}"
    ), "UUID should match expected format"


eval_vals = {
    "x": [1.0, 2.0],
    "mf": 13.0,
}


def test_coco_eval():
    """
    Test that COCOFilter allows COCOEval and updates state correctly.
    """
    filter = COCOFilter(trigger_nth=2)

    coco_record = COCOEval(**eval_vals)
    log_record = makeLogRecord({"msg": coco_record})
    with pytest.raises(AssertionError):
        filter.filter(log_record)
    assert filter.f_evals == 0, "Function evaluations should be 0 after start"

    start_record = COCOStart(**start_vals)
    start_log_record = makeLogRecord({"msg": start_record})
    filter.filter(start_log_record)  # Set up the header state

    assert not filter.filter(
        log_record
    ), "COCOEval should not be allowed due to trigger"
    assert filter.f_evals == 1, "Function evaluations should be incremented"
    assert filter.g_evals == 0, "Gradient evaluations should remain 0"
    assert filter.best_mf == eval_vals["mf"], "Best measured fitness should be updated"
    assert not hasattr(log_record, "log"), "Log record should not be created yet"

    assert filter.filter(log_record), "COCOEval should be allowed on second call"
    assert filter.f_evals == 2, "f_evals should be set to 2 after second call"
    assert filter.g_evals == 0, "g_evals should remain 0"
    assert log_record.log.f_evals == 2, "f_evals should be set in log record"
    assert log_record.log.g_evals == 0, "g_evals should remain 0"
