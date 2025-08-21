# integration test for coco logging
import logging
import os.path as osp
import pytest
from ttex.log.handler import ManualRotatingFileHandler
import shutil
import cocopp
from ttex.log.record import COCOStart, COCOEval, COCOEnd
from ttex.log.filter import COCOLoggerFilter, COCOHandlerFilter
from ttex.log.formatter import KeyFormatter


def test_coco_logging():
    """
    Integration test for COCO logging.
    """

    logger = logging.getLogger("coco_logger")
    logger.setLevel(logging.DEBUG)

    # Create a ManualRotatingFileHandler instance for log and info
    for type_str in ["log", "info"]:
        filepath = osp.join("test_dir", f"coco_{type_str}.txt")
        handler = ManualRotatingFileHandler(filepath=filepath, key=type_str, mode="a")
        formatter = KeyFormatter(key=type_str)
        handler.setFormatter(formatter)
        filter = COCOHandlerFilter(key=type_str)
        handler.addFilter(filter)
        logger.addHandler(handler)

    # Create logger filter
    filter = COCOLoggerFilter(
        trigger_nth=2,
        trigger_imp=0.1,
        trigger_targets=[0.05, 0.1],
    )
    logger.addFilter(filter)

    # Test COCOStart
    start_record = COCOStart(
        fopt=1.0,
        algo="test_algo",
        problem=1,
        dim=2,
        inst=3,
        exp_id="exp_123",
        suite="bbob",
    )

    # Log the start record
    logger.info(start_record)

    logger.info(COCOEval(x=[1.0, 2.0], mf=3.0))
    logger.info(COCOEval(x=[1.0, 2.0], mf=4.0))
    logger.info(COCOEnd())

    # Close all handlers of the logger
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    for type_str in ["log", "info"]:
        filepath = osp.join("test_dir", f"coco_{type_str}.txt")
        print(filepath)
        assert not osp.exists(filepath), f"{type_str} dummy log file retained"

    # Check if the log files are Create
    assert osp.exists(
        osp.join(
            f"{start_record.algo}",
            f"data_{start_record.problem}",
            f"{start_record.exp_id}_{start_record.problem}_d{start_record.dim}.dat",
        )
    ), "COCO log file not created"
    assert osp.exists(
        osp.join(f"{start_record.algo}", f"f{start_record.problem}.info")
    ), "COCO info file not created"
    ## check with cocopp
    res = cocopp.main("test_algo")
    print(res)
