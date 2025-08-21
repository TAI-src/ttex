from ttex.log.record import LoggingState
import numpy as np
import os.path as osp


class COCOLog:
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
        super().__init__()


class COCOEnd(COCOLog):
    pass


class COCOStart(COCOLog):
    def __init__(
        self,
        fopt: float,
        algo: str,
        problem: int,
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
            problem (int): Problem id.
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
        super().__init__()


class COCOState(LoggingState):
    def __init__(self, coco_start: COCOStart):
        self.f_evals = 0
        self.g_evals = 0
        self.best_mf = np.inf
        self.fopt = coco_start.fopt
        # TODO: figure out nicer
        self.dat_filepath = None
        self.inst = coco_start.inst
        self.coco_start = coco_start
        self.best_dist_opt = None
        self.last_imp = None

    def set_dat_filepath(self, dat_filepath: str, info_filepath: str):
        self.dat_filepath = osp.relpath(dat_filepath, start=osp.dirname(info_filepath))

    def update(self, coco_eval: COCOEval):
        self.f_evals += 1
        best_dist_prev = self.best_mf - self.fopt
        self.best_mf = min(self.best_mf, coco_eval.mf)
        self.best_dist_opt = self.best_mf - self.fopt
        assert self.best_dist_opt >= 0
        self.last_imp = best_dist_prev - self.best_dist_opt
