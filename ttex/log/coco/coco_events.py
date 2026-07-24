from dataclasses import dataclass
from uuid import uuid4

from ttex.log.filter import LogEvent


@dataclass(frozen=True)
class COCOEval(LogEvent):
    x: list[float]  # point in search space
    mf: float  # measured fitness


@dataclass(frozen=True)
class COCOEnd(LogEvent):
    pass


@dataclass(frozen=True)
class COCOStart(LogEvent):
    algo: str  # algorithm name
    problem: int  # problem id
    suite: str  # suite name
    exp_id: str = str(uuid4())  # experiment id, defaults to random uuid
    algo_info: str = ""  # additional algorithm info
    fopt: float | None = None  # optimal fitness value (if known)
    dim: int = 0  # search space dimension
    inst: int = 0  # instance id


# TODO: potentially add a transform to know the "inner function" fitness value
# for appropriate comparison of targets across instances
