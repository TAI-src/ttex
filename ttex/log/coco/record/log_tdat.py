from ttex.log.coco.record import COCOLogRecord, COCOLogHeader
from ttex.log.coco import COCOState
from typing import Optional


class COCOtdatRecord(COCOLogRecord):
    def emit(self, trigger_targets: Optional[list[float]]) -> bool:  # type: ignore[override]
        if not trigger_targets:
            return False
        assert (
            self.best_dist_opt is not None
        ), "best_dist_opt must be set before checking targets"
        if self.best_dist_opt <= trigger_targets[0]:
            # Next target reached.
            trigger_targets.pop(0)
            return True
        return False


class COCOtdatHeader(COCOLogHeader):
    def __init__(self, state: COCOState):
        """
        Initialize a COCO dat header with the optimal function value.

        Args:
            state (COCOState): The current state of the COCO logging.
        """
        super().__init__(state, file_type="tdat")
