from ttex.log.coco import COCOEnd, COCOEval, COCOStart, COCOState
from ttex.log.filter import KeySplitter, LogEvent
from ttex.log.filter.event_keysplit_filter import LoggingState
from ttex.log.formatter import StrRecord
from ttex.log.coco.record import (
    COCOInfoHeader,
    COCOInfoRecord,
    COCOdatHeader,
    COCOdatRecord,
    COCOtdatHeader,
    COCOtdatRecord,
)
from cocopp.testbedsettings import SuiteClass
from typing import List, Dict, Optional


class COCOKeySplitter(KeySplitter):
    def __init__(
        self,
        trigger_targets: Optional[List[float]] = None,
        base_evaluation_triggers: Optional[List[int]] = None,
        number_evaluation_triggers: int = 20,
    ):
        self.start_trigger_targets = (
            trigger_targets if trigger_targets is not None else []
        )
        self.base_evaluation_triggers = base_evaluation_triggers
        self.number_evaluation_triggers = number_evaluation_triggers

    def _reset_triggers(self, suite: str):
        if not self.start_trigger_targets:
            try:
                suite_class = SuiteClass(suite)
                self.trigger_targets = list(
                    suite_class.settings["pprldmany_target_values"]
                )
            except ValueError:
                self.trigger_targets = []
        else:
            self.trigger_targets = self.start_trigger_targets.copy()
        self.trigger_targets.sort(reverse=True)

    def process(self, state: LoggingState, event: LogEvent) -> Dict[str, StrRecord]:
        assert isinstance(state, COCOState)
        return_dict: Dict[str, StrRecord] = {}

        if isinstance(event, COCOStart):
            self._reset_triggers(event.suite)
            info_header = COCOInfoHeader(state)
            log_dat_header = COCOdatHeader(state)
            log_tdat_header = COCOtdatHeader(state)
            state.set_dat_filepath(log_dat_header.filepath, info_header.filepath)
            if info_header.emit():
                return_dict["info"] = info_header
            if log_dat_header.emit():
                return_dict["log_dat"] = log_dat_header
            if log_tdat_header.emit():
                return_dict["log_tdat"] = log_tdat_header
        elif isinstance(event, COCOEval):
            log_dat_record = COCOdatRecord(state)
            log_tdat_record = COCOtdatRecord(state)
            if log_dat_record.emit(
                base_evaluation_triggers=self.base_evaluation_triggers,
                number_evaluation_triggers=self.number_evaluation_triggers,
                last_dat_emit=None,
            ):
                # explicitly not the last eval
                return_dict["log_dat"] = log_dat_record
                state.last_dat_emit = state.f_evals
            if log_tdat_record.emit(self.trigger_targets):
                return_dict["log_tdat"] = log_tdat_record
        elif isinstance(event, COCOEnd):
            # Emit last evaluation if not already done
            log_dat_record = COCOdatRecord(state)
            if log_dat_record.emit(
                base_evaluation_triggers=self.base_evaluation_triggers,
                number_evaluation_triggers=self.number_evaluation_triggers,
                last_dat_emit=state.last_dat_emit,
            ):
                return_dict["log_dat"] = log_dat_record
            info_record = COCOInfoRecord(state)
            if info_record.emit():
                return_dict["info"] = info_record
        return return_dict

    def init_logging_state(self) -> COCOState:
        return COCOState()
