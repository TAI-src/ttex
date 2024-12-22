from ttex.config import Config
from .. import dummy_log_handler
from typing import Union, List, Tuple
from enum import Enum


class DummyEnum(Enum):
    A = 1
    B = 2


class DummyConfig(Config):
    def __init__(
        self,
        a: int,
        b: Union[Config, str],
        c: List[str] = [""],
        d: Tuple[str, int] = ("", 3),
        e: DummyEnum = DummyEnum.A,
    ):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.test = "test"


class EmptyConfig(Config):
    def __init__(self):
        pass


dict_config = {
    "DummyConfig": {
        "a": "a",
        "b": {
            "DummyConfig": {
                "a": "a2",
                "b": "b2",
            }
        },
        "c": "ConfigFactory",
        "d": ["d", 4],
        "e": "DummyEnum.B",
    }
}
