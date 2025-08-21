from ttex.log.filter import COCOHandlerFilter
from ttex.log.record import COCOEval, COCOStart, COCOEnd
from ..handler.test_manual_rotating_file_handler import DummyRecord, DummyHeader
from logging import makeLogRecord
import pytest


def test_filter_not_coco():
    """
    Test that the filter does not allow non-COCOLog records.
    """
    filter = COCOHandlerFilter(key="test_key")
    record = makeLogRecord({"msg": "This is not a COCOLog"})
    assert not filter.filter(record)


def make_coco_log(key: str):
    if key == "start":
        return COCOStart(
            fopt=0.0,
            algo="test_algo",
            problem=1,
            dim=2,
            inst=3,
            exp_id="test_exp",
            suite="test_suite",
        )
    elif key == "end":
        return COCOEnd()
    elif key == "eval":
        return COCOEval(x=[0.1, 0.2, 0.3], mf=0.5)
    else:
        raise ValueError(f"Unknown COCO log type: {key}")


@pytest.mark.parametrize("type", ["start", "end", "eval"])
def test_coco_types(type):
    """
    Test that the filter allows COCOEval records with the correct key.
    """
    filter = COCOHandlerFilter(key="test_key")
    coco_log_obj = make_coco_log(type)
    dummy_record = DummyRecord(val=1)
    record = makeLogRecord({"msg": coco_log_obj, "test_key": dummy_record})

    assert filter.filter(record) is True


def test_coco_header():
    """
    Test that the filter allows COCOHeader records with the correct key.
    """
    filter = COCOHandlerFilter(key="test_key")
    dummy_header = DummyHeader(val=1, uuid="1234")
    coco_eval = COCOEval(x=[0.1, 0.2, 0.3], mf=0.5)
    record = makeLogRecord({"msg": coco_eval, "test_key": dummy_header})

    assert filter.filter(record) is True
    # second time has same uuid, should be False
    assert filter.filter(record) is False

    dummy_header._uuid = "5678"  # Change UUID
    record = makeLogRecord({"msg": coco_eval, "test_key": dummy_header})
    assert filter.filter(record) is True  # Now it should be True again with new UUID
