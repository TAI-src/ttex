# integration test for coco logging
import logging
import os.path as osp
from ttex.log.handler import ManualRotatingFileHandler
import cocopp
from ttex.log.formatter import KeyFormatter
from ttex.log.filter import KeyFilter, EventKeysplitFilter
from ttex.log.coco import COCOStart, COCOEval, COCOEnd
import numpy as np
from cocopp.pproc import DictAlg
import shutil
import pytest


def get_dummy_start_params(problem: int = 3, dim: int = 2, inst: int = 2) -> dict:
    return {
        "fopt": np.random.randn() * 100,
        "algo": "test_algo",
        "problem": problem,
        "dim": dim,
        "inst": inst,
        "suite": "bbob",
        "exp_id": "test_exp_id",
    }


def generate_events(num_evals: int, problem: int, dim: int, inst: int):
    events = []
    start_record = COCOStart(**get_dummy_start_params(problem, dim, inst))
    events.append(start_record)
    for _ in range(num_evals):
        x = np.random.rand(dim)
        mf = np.random.rand() + start_record.fopt
        events.append(COCOEval(x=x.tolist(), mf=mf))
    events.append(COCOEnd())
    return events


# TODO: test multiple instances, dimensions and functions


@pytest.fixture(scope="function", autouse=True)
def cleanup_dummy_files():
    shutil.rmtree("test_algo", ignore_errors=True)
    shutil.rmtree("test_dir", ignore_errors=True)
    shutil.rmtree("ppdata", ignore_errors=True)

    yield

    shutil.rmtree("test_algo", ignore_errors=True)
    shutil.rmtree("test_dir", ignore_errors=True)
    shutil.rmtree("ppdata", ignore_errors=True)


def def_setup_manual():
    """
    Integration test for COCO logging.
    """
    # TODO: make this into a default setup to make it easier
    logger = logging.getLogger("coco_logger1")
    logger.setLevel(logging.INFO)

    splitter_args = {
        "trigger_nth": 2,
    }
    coco_filter = EventKeysplitFilter(
        key_splitter_cls="ttex.log.coco.COCOKeySplitter",
        key_splitter_args=splitter_args,
    )
    logger.addFilter(coco_filter)

    # Create a ManualRotatingFileHandler instance for log and info
    for type_str in ["info", "log_dat", "log_tdat"]:
        # Make some dummy files that should be deleted after
        filepath = osp.join("test_dir", f"coco_{type_str}.txt")
        handler = ManualRotatingFileHandler(filepath=filepath, key=type_str, mode="a")
        formatter = KeyFormatter(key=type_str)
        handler.setFormatter(formatter)
        filter = KeyFilter(key=type_str)
        handler.addFilter(filter)
        logger.addHandler(handler)
    return logger


def simulate_once(logger, num_evals: int, problem: int, dim: int, inst: int):
    events = generate_events(num_evals, problem, dim, inst)
    for event in events:
        logger.info(event)

    return events[0]  # return start record for further checks


def check_files_exist(start_record: COCOStart):
    for type_str in ["info", "log_dat", "log_tdat"]:
        # Check if the dummy files are deleted
        filepath = osp.join("test_dir", f"coco_{type_str}.txt")
        assert not osp.exists(filepath), f"{type_str} dummy log file retained"
    # Check if the log files are created
    log_file_base = osp.join(
        f"{start_record.algo}",
        f"data_{start_record.problem}",
        f"{start_record.exp_id}_{start_record.problem}_d{start_record.dim}_i{start_record.inst}",
    )
    assert osp.exists(f"{log_file_base}.dat"), "COCO dat log file not created"
    assert osp.exists(f"{log_file_base}.tdat"), "COCO tdat log file not created"
    # Check that tdat file has at least one record (more than just header)
    with open(
        f"{log_file_base}.tdat",
        "r",
    ) as f:
        lines = f.readlines()
        assert len(lines) > 1, "COCO tdat log file is empty"

    assert osp.exists(
        osp.join(
            f"{start_record.algo}", f"f{start_record.problem}_i{start_record.inst}.info"
        )
    ), "COCO info file not created"


def test_coco_logging_integration():
    logger = def_setup_manual()
    start_records = [None] * 4
    start_records[0] = simulate_once(logger, num_evals=50, problem=3, dim=2, inst=2)
    start_records[1] = simulate_once(logger, num_evals=30, problem=3, dim=2, inst=3)
    start_records[2] = simulate_once(logger, num_evals=30, problem=3, dim=3, inst=4)
    start_records[3] = simulate_once(logger, num_evals=30, problem=5, dim=2, inst=2)
    # Close handlers and remove from logger
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    # Check files exist for first start record
    for start_rec in start_records:
        assert isinstance(start_rec, COCOStart)
        check_files_exist(start_rec)
    ## check with cocopp
    res = cocopp.main("test_algo")
    assert isinstance(res, DictAlg)
    print(res)
    result_dict = res[("test_algo", "")][0]
    print(result_dict)
    assert result_dict.funcId == 3
    assert result_dict.dim == 2
    assert result_dict.algId == "test_algo"
    assert len(result_dict.instancenumbers) == 2  # 2,3
    assert result_dict.instancenumbers[0] == 2
