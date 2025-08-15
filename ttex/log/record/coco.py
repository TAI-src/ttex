from ttex.log.record import Record
from abstract import ABC


class COCOLog(ABC):
    pass


class COCOEval(COCOLog):
    """
    Represents a COCO evaluation record.
    This class is used to store the results of a COCO evaluation step.
    """

    def __init__(self, x: list[float], mf: float):
        """
        Initialize a COCO evaluation record with decision variables and measured fitness.

        Args:
            x (list): List of decision variable values.
            mf (float): Measured fitness value.
        """
        self.x = x
        self.mf = mf


class COCOEnd(COCOLog):
    pass


class COCOStart(COCOLog):
    def __init__(
        self,
        fopt: float,
        algo: str,
        problem: str,
        dim: int,
        inst: int,
        exp_id: str,
        suite: str,
    ):
        """
        Initialize a COCO start record with problem and algorithm details.

        Args:
            fopt (float): Optimal function value.
            algo (str): Algorithm name.
            problem (str): Problem name.
            dim (int): Dimension of the problem.
            inst (int): Instance number.
            exp_id (str): Experiment ID.
            suite (str): Suite name.
        """
        self.fopt = fopt
        self.algo = algo
        self.problem = problem
        self.dim = dim
        self.inst = inst
        self.exp_id = exp_id
        self.suite = suite
