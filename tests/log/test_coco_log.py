# integration test for coco logging
import logging
import os.path as osp
import pytest
from ttex.log.record import COCORecord, COCOHeader
from .test_coco_record import coco_header_vals
from ttex.log.handler import ManualRotatingFileHandler
import shutil
from ttex.log.filter import COCOFilter
import cocopp


@pytest.fixture(autouse=True, scope="module")
def remove_test_files():
    """
    Fixture to remove test files before and after the tests.
    """
    shutil.rmtree(coco_header_vals["algo"], ignore_errors=True)

    yield  # run the tests

    # Cleanup after tests
    # shutil.rmtree(coco_header_vals["algo"], ignore_errors=True)


def test_coco_logging():
    """
    Integration test for COCO logging.
    """
    # Create a ManualRotatingFileHandler instance
    filepath = osp.join("test_dir", "coco_log.txt")
    handler = ManualRotatingFileHandler(filepath=filepath, mode="a")

    # Create a filter
    filter = COCOFilter(trigger_nth=2)
    handler.addFilter(filter)

    logger = logging.getLogger("coco_logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    header = COCOHeader(**coco_header_vals)
    record = COCORecord(x=[1.0, 2.0], mf=3)

    # Log the header
    logger.info(header)
    # Log the record
    logger.info(record)
    logger.info(record)
    logger.info(record)
    logger.info(record)
    logger.info(record)
    handler.close()

    assert not osp.exists(filepath), "dummy log file retained"
    # Check if the log file was Create
    assert osp.exists(header.filepath), "Header file not created"

    with open(header.filepath, "r") as f:
        lines = f.readlines()
        assert len(lines) == 3, "header + 2 records expected"
        assert lines[0].strip() == str(header), "Header not formatted correctly"

    ## check with cocopp
    res = cocopp.main(coco_header_vals["algo"])
    print(res)
