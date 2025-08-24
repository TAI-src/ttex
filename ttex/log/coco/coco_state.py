from ttex.log.filter import LoggingState, LogEvent
from ttex.log.coco import COCOEval, COCOStart, COCOEnd
import numpy as np
import os.path as osp


class COCOState(LoggingState):
    def __init__(self):
        self._needs_start = True
        super().__init__()

    def update(self, event: LogEvent) -> None:
        if isinstance(event, COCOStart):
            self._update_start(event)
        elif isinstance(event, COCOEval):
            self._update_eval(event)
        elif isinstance(event, COCOEnd):
            self._needs_start = True
            # COCOEnd does not require any specific state update
        else:
            raise ValueError(
                "COCOState can only process COCOStart, COCOEval, and COCOEnd events"
            )

    def _update_start(self, coco_start: COCOStart) -> None:
        self.f_evals = 0
        self.g_evals = 0
        self.best_mf = np.inf
        self.fopt = coco_start.fopt
        self.inst = coco_start.inst
        self.coco_start = coco_start
        self.best_dist_opt = None
        self.last_imp = None
        self._needs_start = False

    def _update_eval(self, coco_eval: COCOEval) -> None:
        assert not self._needs_start, "COCOStart must be processed before COCOEval"
        self.f_evals += 1
        best_dist_prev = self.best_mf - self.fopt
        self.best_mf = min(self.best_mf, coco_eval.mf)
        self.best_dist_opt = self.best_mf - self.fopt
        assert self.best_dist_opt >= 0
        self.last_imp = best_dist_prev - self.best_dist_opt
        self.last_eval = coco_eval

    def set_dat_filepath(self, dat_filepath: str, info_filepath: str):
        self.dat_filepath = osp.relpath(dat_filepath, start=osp.dirname(info_filepath))
