from uuid import uuid4
from ttex.log.filter import LogEvent
from dataclasses import dataclass


@dataclass(frozen=True)
class COCOEval(LogEvent):
    x: list[float]
    mf: float


@dataclass(frozen=True)
class COCOEnd(LogEvent):
    pass


@dataclass(frozen=True)
class COCOStart(LogEvent):
    fopt: float
    algo: str
    problem: int
    dim: int
    inst: int
    suite: str
    exp_id: str = str(uuid4())
