from ttex.log.coco.record import COCOLogRecord, COCOLogHeader
from ttex.log.coco import COCOState
from typing import Optional, List
import math


class COCOdatRecord(COCOLogRecord):
    @staticmethod
    def ceil_to_target(value: float, improvement_step: float = 1e-5) -> float:
        return math.ceil(value / improvement_step) * improvement_step

    def improvement_trigger(self, improvement_step: float) -> bool:
        """
        Check if a new target has been reached based on the last improvement.
        Args:
            improvement_step (float): The step size for improvement targets.
        Returns:
            bool: True if a new target has been reached, False otherwise.
        """
        assert (
            self.last_imp is not None and self.last_imp > 0
        ), "last_imp must be positive to check for improvement"
        new_target_reached = COCOdatRecord.ceil_to_target(self.mf, improvement_step)
        prev_target_reached = COCOdatRecord.ceil_to_target(
            self.mf + self.last_imp, improvement_step
        )
        if new_target_reached < prev_target_reached:
            # New target reached.
            return True
        else:
            return False

    def log_target_trigger(
        self, number_target_triggers: int, target_precision: float = 1e-8
    ) -> bool:
        if self.best_dist_opt is None or self.best_dist_opt < target_precision:
            # No best distance to optimum recorded or already within precision of optimum
            return False
        else:  # Check if a new target has been reached based on the last improvement.
            assert (
                self.last_imp is not None and self.last_imp > 0
            ), "last_imp must be positive to check for target triggers"
            new_value = COCOdatRecord.get_exp_bin(
                number_target_triggers, self.best_dist_opt
            )
            prev_value = COCOdatRecord.get_exp_bin(
                number_target_triggers, self.best_dist_opt + self.last_imp
            )
            return new_value < prev_value

    def emit(
        self,
        improvement_step: float = 1e-5,
        number_target_triggers: int = 20,
        target_precision: float = 1e-8,
    ) -> bool:  # type: ignore[override]
        assert self.f_evals > 0, "No evaluations have been recorded"
        if self.f_evals == 1:
            # Always log the first evaluation
            return True
        if self.last_imp is None or self.last_imp <= 0:
            # No improvement in the last evaluation, therefore has not hit any new targets
            return False
        if improvement_step > 0:
            improvement_trigger = self.improvement_trigger(improvement_step)
        else:
            improvement_trigger = False
        if number_target_triggers > 0 and target_precision > 0:
            log_target_trigger = self.log_target_trigger(
                number_target_triggers, target_precision
            )
        else:
            log_target_trigger = False
        return improvement_trigger or log_target_trigger


class COCOdatHeader(COCOLogHeader):
    def __init__(self, state: COCOState):
        """
        Initialize a COCO dat header with the optimal function value.

        Args:
            state (COCOState): The current state of the COCO logging.
        """
        super().__init__(state, file_type="dat")
