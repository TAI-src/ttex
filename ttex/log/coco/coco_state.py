from ttex.log.filter import LoggingState, LogEvent
from ttex.log.coco import COCOEval, COCOStart, COCOEnd
import numpy as np
import os.path as osp
from typing import Optional


class COCOState(LoggingState):
    def __init__(self):
        self._needs_start = True
        self.last_tdat_emit = 0
        self.best_target = None
        super().__init__()

    def update(self, event: LogEvent) -> None:
        if isinstance(event, COCOStart):
            self._update_start(event)
        elif isinstance(event, COCOEval):
            self._update_eval(event)
        elif isinstance(event, COCOEnd):
            self._update_end(event)
        else:
            raise ValueError(
                "COCOState can only process COCOStart, COCOEval, and COCOEnd events"
            )

    def _update_start(self, coco_start: COCOStart) -> None:
        self.f_evals = 0  # Number of evaluations
        self.g_evals = 0  # Number of constraint evaluations (not currently supported)
        self.best_mf = np.inf  # Best observed function value
        self.fopt = coco_start.fopt  # Optimal function value (if known)
        self.inst = coco_start.inst  # Problem instance number
        self.coco_start = coco_start  # Store the COCOStart event
        self.best_diff_opt: Optional[float] = None  # Best difference to optimal value
        self.last_imp: Optional[
            float
        ] = None  # Improvement of best_mf since last evaluation
        self._needs_start = False  # State now expects new COCOStart event
        self.last_tdat_emit = 0  # Last evaluation count when .tdat was emitted
        self.best_target = None  # Best target reached (from .dat logging)

    def _update_eval(self, coco_eval: COCOEval) -> None:
        assert not self._needs_start, "COCOStart must be processed before COCOEval"
        assert len(coco_eval.x) == self.coco_start.dim
        self.f_evals += 1
        self.last_imp = max(
            self.best_mf - coco_eval.mf, 0
        )  # positive or zero (minimisation)
        self.best_mf = min(self.best_mf, coco_eval.mf)
        if self.fopt is not None:
            self.best_diff_opt = self.best_mf - self.fopt
        else:
            self.best_diff_opt = self.best_mf  # If fopt is unknown, use best_mf
        self.last_eval = coco_eval

    def _update_end(self, coco_end: COCOEnd) -> None:
        self._needs_start = True

    def set_dat_filepath(self, dat_filepath: str, info_filepath: str):
        self.dat_filepath = osp.relpath(dat_filepath, start=osp.dirname(info_filepath))
