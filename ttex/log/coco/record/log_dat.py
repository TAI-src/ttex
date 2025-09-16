from ttex.log.coco.record import COCOLogRecord, COCOLogHeader
from ttex.log.coco import COCOState
from typing import Optional


class COCOdatRecord(COCOLogRecord):
    def emit(
        self,
        trigger_nth: int,
        last_dat_emit: Optional[int] = None,  # only pass when emitting the last record
    ) -> bool:  # type: ignore[override]
        """
        Check if the record should be emitted based on the trigger_nth condition.
        """
        if (
            last_dat_emit and self.f_evals > last_dat_emit
        ):  # Emit the last evaluation unless already done
            return True
        if self.f_evals == 1 and not last_dat_emit:
            # Always emit the first evaluation (unless it is also the last)
            return True
        if trigger_nth <= 0:
            return False
        else:
            return self.f_evals % trigger_nth == 0


class COCOdatHeader(COCOLogHeader):
    def __init__(self, state: COCOState):
        """
        Initialize a COCO dat header with the optimal function value.

        Args:
            state (COCOState): The current state of the COCO logging.
        """
        super().__init__(state, file_type="dat")
