from ttex.log.record import COCOHeader, COCORecord
from ttex.log.filter import COCOFilter
from logging import makeLogRecord
from .test_coco_record import coco_header_vals
import pytest


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


def test_filter_coco_header():
    """Test that COCOFilter allows COCOHeader and resets state."""
    filter = COCOFilter()
    assert filter.current_uuid is None, "Initial UUID should be None"
    assert filter.f_opt is None, "Initial f_opt should be None"
    filter.f_evals = 5  # Set some initial evaluations

    header = COCOHeader(**coco_header_vals)
    record = makeLogRecord({"msg": header})

    assert filter.filter(record), "COCOHeader should be allowed"
    assert (
        filter.current_uuid == header.uuid
    ), "Current UUID should be set to header UUID"
    assert filter.f_opt == header.fopt, "f_opt should be set from header"
    assert filter.f_evals == 0, "Function evaluations should be reset to 0"
    assert filter.g_evals == 0, "Gradient evaluations should be reset to 0"
    assert filter.best_mf == float(
        "inf"
    ), "Best measured fitness should be initialized to infinity"


def test_filter_coco_record():
    """
    Test that COCOFilter allows COCORecord and updates state.
    """
    filter = COCOFilter(trigger_nth=2)

    record_msg = COCORecord(x=[1.0, 2.0], mf=3.0)
    record = makeLogRecord({"msg": record_msg})
    with pytest.raises(
        AssertionError, match="f_opt must be set in COCOHeader before COCORecord."
    ):
        filter.filter(record)
    assert record_msg.f_evals is None, "f_evals should be None initially"

    header = COCOHeader(**coco_header_vals)
    header_record = makeLogRecord({"msg": header})
    filter.filter(header_record)  # Set up the header state

    assert not filter.filter(record), "COCORecord should not be allowed due to trigger"
    assert filter.f_evals == 1, "Function evaluations should be incremented"
    assert filter.g_evals == 0, "constraint evaluations should remain 0"
    assert filter.best_mf == record_msg.mf, "Best measured fitness should be updated"
    assert record_msg.f_evals is None, "f_evals should be still None if not emitted"

    assert filter.filter(record)  # Second call to trigger the nth evaluations
    assert record_msg.f_evals == 2, "f_evals should be set to 2 after second call"
    assert record_msg.g_evals == 0, "g_evals should remain 0"
