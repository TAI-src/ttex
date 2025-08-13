import logging
from ttex.log.handler import ManualRotatingFileHandler
from ttex.log.record import Record, Header
import os.path as osp

class DummyRecord(Record):
    def __init__(self, val:int):
        self.val = val
    def __str__(self):
        return f"DummyRecord(val={self.val})"

class DummyHeader(Header):
    def __init__(self, val:float):
        self.val = val
    def __str__(self):
        return f"DummyHeader(val={self.val})"

    @property
    def filepath(self) -> str:
        return osp.join("test_dir", "header_file.txt")

def test_manual_rotating_file_handler():
    """
    Test the ManualRotatingFileHandler by logging a message and checking if it is emitted correctly.
    """
    handler = ManualRotatingFileHandler(filepath=
                                        osp.join("test_dir", "test_file.txt"),
                                        mode="a")
    logger = logging.getLogger("test_manual_rotating_file_handler")
    logger.setLevel(logging.DEBUG)
    
    logger.addHandler(handler)
    
    # Log a test message
    logger.info(DummyHeader(3.14))
    logger.info(DummyRecord(42))
    
    # Clean up
    handler.close()


