import numpy as np
from logging import Filter
from typing import Optional
from ttex.log.record import (
    COCOStart,
    COCOEnd,
    COCOEval,
    COCOLogRecord,
    COCOLogHeader,
    COCOInfoRecord,
    COCOInfoHeader,
    COCOLog,
)
import os.path as osp


class COCOLoggerFilter(Filter):
    """
    Filter to allow only COCOHeader and COCORecord messages.
    """

    def __init__(
        self,
        trigger_nth: int = 1,
        trigger_imp: Optional[float] = None,
        trigger_targets: Optional[list[float]] = None,
        name: str = "COCOFilter",
    ):
        """
        Initialize the COCOFilter with an optional name.
        """
        # TODO: add parameters for triggers
        self.f_evals = 0
        self.g_evals = 0
        self.best_mf = np.inf
        self.f_opt = None
        self.log_filepath = None
        self.inst = None
        # TODO: maybe retain past uuids

        # Trigger parameters
        self.trigger_nth = trigger_nth
        self.trigger_imp = trigger_imp
        self.trigger_targets = trigger_targets if trigger_targets is not None else []
        self.trigger_targets.sort(reverse=True)  # Sort targets for efficient checking
        super().__init__(name)

    def trigger_nth_eval(self, f_evals: int):
        """
        Check if the COCORecord should be emitted based on the trigger_nth condition.
        If trigger_nth is 0, it always returns False.
        Args:
            f_evals (int): The number of function evaluations.
        Returns:
            bool: True if the COCORecord should be emitted, False otherwise.
        """
        if self.trigger_nth <= 0:
            return False
        else:
            return f_evals % self.trigger_nth == 0

    def trigger_imp_eval(self, imp: float):
        """
        Check if the improvement is significant enough to trigger an emit.
        If trigger_imp is None, it always returns False.
        Args:
            imp (float): The improvement value to check.
        Returns:
            bool: True if the improvement is significant enough to trigger an emit, False otherwise.
        """
        if not self.trigger_imp:
            return False
        else:
            return imp >= self.trigger_imp

    def trigger_target_eval(self, best_dist_opt: float):
        """
        Check if the best distance to the optimal function value is within the trigger targets.
        If trigger_targets is empty, it always returns False.
        Args:
            best_dist_opt (float): The best distance to the optimal function value.
        Returns:
            bool: True if the best distance is within the trigger targets, False otherwise.
        """
        if not self.trigger_targets:
            return False
        if best_dist_opt <= self.trigger_targets[0]:
            # Next target reached.
            self.trigger_targets.pop(0)
            return True
        return False

    def trigger_emit(self, imp: float, f_evals: int, best_dist_opt: float):
        """
        Check if the COCORecord should be emitted based on the triggers.
        Args:
            imp (float): The improvement value.
            f_evals (int): The number of function evaluations.
            best_dist_opt (float): The best distance to the optimal function value.
        Returns:
            bool: True if the COCORecord should be emitted, False otherwise.
        """
        return (
            self.trigger_nth_eval(f_evals)
            or self.trigger_imp_eval(imp)
            or self.trigger_target_eval(best_dist_opt)
        )

    def filter(self, record):
        """ """
        if not isinstance(record.msg, COCOLog):
            return False

        if isinstance(record.msg, COCOStart):
            # If it's a new header, reset the current UUID and evaluations
            self.f_opt = record.msg.fopt
            self.f_evals = 0
            self.g_evals = 0
            self.best_mf = np.inf

            info_header = COCOInfoHeader(
                suite=record.msg.suite,
                funcId=record.msg.problem,
                dim=record.msg.dim,
                algId=record.msg.algo,
            )
            log_header = COCOLogHeader(
                fopt=record.msg.fopt,
                algo=record.msg.algo,
                problem=record.msg.problem,
                dim=record.msg.dim,
                inst=record.msg.inst,
                exp_id=record.msg.exp_id,
            )
            record.info = info_header
            record.log = log_header
            # TODO: make path relative from info file
            self.log_filepath = osp.relpath(
                log_header.filepath, start=osp.dirname(info_header.filepath)
            )
            self.inst = record.msg.inst

            return True
        elif isinstance(record.msg, COCOEval):
            assert (
                self.f_opt is not None
            ), "f_opt must be set in COCOHeader before COCORecord."
            self.f_evals += 1
            best_dist_prev = self.best_mf - self.f_opt
            self.best_mf = min(self.best_mf, record.msg.mf)
            best_dist_opt = self.best_mf - self.f_opt
            assert (
                best_dist_opt >= 0
            ), f"best_dist_opt must be non-negative, got {best_dist_opt}."
            imp = best_dist_prev - best_dist_opt

            # Check if the record should be emitted based on the triggers
            if not self.trigger_emit(imp, self.f_evals, best_dist_opt):
                return False

            log_record = COCOLogRecord(
                x=record.msg.x,
                mf=record.msg.mf,
                f_evals=self.f_evals,
                g_evals=self.g_evals,
                best_dist_opt=best_dist_opt,
                best_mf=self.best_mf,
            )
            record.log = log_record

            return True
        elif isinstance(record.msg, COCOEnd):

            assert (
                self.f_opt is not None
            ), "f_opt must be set in COCOHeader before COCOEnd."
            assert (
                self.log_filepath is not None
            ), "log_filepath must be set in COCOHeader before COCOEnd."
            assert (
                self.inst is not None
            ), "inst must be set in COCOHeader before COCOEnd."
            ## emit cocoinfo record
            info_record = COCOInfoRecord(
                file_path=self.log_filepath,
                inst=self.inst,
                f_evals=self.f_evals,
                prec=self.best_mf - self.f_opt,
            )
            record.info = info_record
            return True

        return False
