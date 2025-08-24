from ttex.log.coco import COCOEnd, COCOEval, COCOStart, COCOState
from ttex.log.filter import KeySplitter, LogEvent
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


class COCOKeySplitter(KeySplitter):
    def __init__(
        self, trigger_nth: int = 1, trigger_targets: list[float] | None = None
    ):
        self.trigger_nth = trigger_nth
        self.start_trigger_targets = (
            trigger_targets if trigger_targets is not None else []
        )

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

    def process(self, state: COCOState, event: LogEvent) -> dict[str, list[StrRecord]]:
        return_dict = {}

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
            if log_dat_record.emit(self.trigger_nth):
                return_dict["log_dat"] = log_dat_record
            if log_tdat_record.emit(self.trigger_targets):
                return_dict["log_tdat"] = log_tdat_record
        elif isinstance(event, COCOEnd):
            info_record = COCOInfoRecord(state)
            if info_record.emit():
                return_dict["info"] = info_record
        return return_dict

    def init_logging_state(self) -> COCOState:
        return COCOState()
