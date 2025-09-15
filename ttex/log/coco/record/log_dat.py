from ttex.log.coco.record import COCOLogRecord, COCOLogHeader
from ttex.log.coco import COCOState


class COCOdatRecord(COCOLogRecord):
    def emit(self, trigger_nth: int) -> bool:  # type: ignore[override]
        """
        Check if the record should be emitted based on the trigger_nth condition.
        """
        if self.f_evals == 1:
            # Always emit the first evaluation
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
