from logging import Filter
from typing import Optional
from ttex.log.record import COCOHeader, COCORecord
import numpy as np


class COCOFilter(Filter):
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
        self.current_uuid = None
        self.f_evals = 0
        self.g_evals = 0
        self.best_mf = np.inf
        self.f_opt = None
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
        """
        Override the filter method to allow only COCOHeader and COCORecord.
        """
        if not isinstance(record.msg, (COCOHeader, COCORecord)):
            return False

        if isinstance(record.msg, COCOHeader) and record.msg.uuid != self.current_uuid:
            # If it's a new header, reset the current UUID and evaluations
            self.current_uuid = record.msg.uuid
            self.f_opt = record.msg.fopt
            self.f_evals = 0
            self.g_evals = 0
            self.best_mf = np.inf
            return True
        if isinstance(record.msg, COCORecord):
            assert (
                self.f_opt is not None
            ), "f_opt must be set in COCOHeader before COCORecord."
            self.f_evals += 1
            best_dist_prev = self.best_mf - self.f_opt
            self.best_mf = min(self.best_mf, record.msg.mf)
            best_dist_opt = self.best_mf - self.f_opt
            imp = best_dist_prev - best_dist_opt

            # Check if the record should be emitted based on the triggers
            if not self.trigger_emit(imp, self.f_evals, best_dist_opt):
                return False

            ## fill record
            record.msg.f_evals = self.f_evals
            record.msg.g_evals = self.g_evals
            record.msg.best_dist_opt = best_dist_opt
            record.msg.best_mf = self.best_mf

            return True

        return False
