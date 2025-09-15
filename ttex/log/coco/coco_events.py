from uuid import uuid4
from ttex.log.filter import LogEvent
from dataclasses import dataclass


@dataclass(frozen=True)
class COCOEval(LogEvent):
    x: list[float]  # point in search space
    mf: float  # measured fitness


@dataclass(frozen=True)
class COCOEnd(LogEvent):
    pass


@dataclass(frozen=True)
class COCOStart(LogEvent):
    fopt: float  # optimal fitness value
    algo: str  # algorithm name
    problem: int  # problem id
    dim: int  # search space dimension
    inst: int  # instance id
    suite: str  # suite name
    exp_id: str = str(uuid4())  # experiment id, defaults to random uuid


# TODO: Handling for and testing with unknown optimum
