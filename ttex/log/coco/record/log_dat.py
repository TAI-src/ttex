from ttex.log.coco.record import COCOLogRecord, COCOLogHeader
from ttex.log.coco import COCOState
from typing import Optional, List
import math


class COCOdatRecord(COCOLogRecord):

    @staticmethod
    def trigger_nth(number_evaluation_triggers: int, f_evals: int) -> bool:
        """
        Determine if the current function evaluation count `f_evals` meets the
        trigger condition based on `number_evaluation_triggers`.

        - every 10**(exponent1/number_of_triggers) for exponent1 >= 0
        See: https://github.com/numbbo/coco/blob/master/code-experiments/src/coco_observer.c
        Args:
            number_evaluation_triggers (int): Number of evaluation triggers.
            f_evals (int): Current function evaluation count.

        Returns:
            bool: True if the trigger condition is met, False otherwise.
        """
        exponent = math.ceil(number_evaluation_triggers * math.log10(f_evals))
        value = math.floor(10 ** (exponent / number_evaluation_triggers))
        return f_evals == value

    @staticmethod
    def base_eval(
        base_evaluation_triggers: List[int], dimension: int, f_evals: int
    ) -> bool:
        """
        Determine if the current function evaluation count `f_evals` meets the
        base evaluation trigger condition.

        - every base_evaluation * dimension * (10**exponent2) for exponent2 >= 0
        See: https://github.com/numbbo/coco/blob/master/code-experiments/src/coco_observer.c
        Args:
            base_evaluation_triggers (List[int]): List of base evaluation triggers.
            dimension (int): Problem dimension.
            f_evals (int): Current function evaluation count.
        Returns:
            bool: True if the trigger condition is met, False otherwise.
        """

        if dimension <= 0:
            return False
        for base in base_evaluation_triggers:
            scaled_eval = f_evals / (dimension * base)
            # check if scaled_eval is a power of 10
            if math.log10(scaled_eval).is_integer():
                return True
        return False

    def emit(  # type: ignore[override]
        self,
        base_evaluation_triggers: List[int] = [1, 2, 5],
        number_evaluation_triggers: int = 20,
        last_dat_emit: Optional[int] = None,  # only pass when emitting the last record
    ) -> bool:  # type: ignore[override]
        """
        Check if the record should be emitted based on the trigger_nth condition.
        """
        assert self.f_evals > 0, "f_evals must be positive to determine emission"
        if (
            last_dat_emit and self.f_evals > last_dat_emit
        ):  # Emit the last evaluation unless already done
            return True
        if self.f_evals == 1 and last_dat_emit is None:
            # Always emit the first evaluation (unless it is also the last)
            return True
        trigger_nth = COCOdatRecord.trigger_nth(
            number_evaluation_triggers, self.f_evals
        )
        trigger_base = COCOdatRecord.base_eval(
            base_evaluation_triggers, self.dim, self.f_evals
        )
        return trigger_nth or trigger_base


class COCOdatHeader(COCOLogHeader):
    def __init__(self, state: COCOState):
        """
        Initialize a COCO dat header with the optimal function value.

        Args:
            state (COCOState): The current state of the COCO logging.
        """
        super().__init__(state, file_type="dat")
