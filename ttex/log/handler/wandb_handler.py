import logging
import ast
from wandb.sdk.wandb_run import Run
from typing import Optional, Dict
from ttex.log import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class WandbHandler(logging.Handler):
    """
    Handler that will emit results to wandb
    """

    def __init__(
        self,
        wandb_run: Run,
        custom_metrics: Optional[Dict] = None,
        level=logging.NOTSET,
    ):
        super().__init__(level)
        self.run = wandb_run
        if custom_metrics:
            for step_metric, metrics in custom_metrics.items():
                self.run.define_metric(step_metric)
                for metric in metrics:
                    self.run.define_metric(metric, step_metric=step_metric)

    def emit(self, record):
        msg = record.getMessage()
        step = record.step if hasattr(record, "step") else None
        commit = record.commit if hasattr(record, "commit") else None

        try:
            msg_dict = ast.literal_eval(msg)
            assert isinstance(msg_dict, dict)
            self.run.log(msg_dict, step=step, commit=commit)
        except SyntaxError as e:
            logger.handle(record)
            logger.warning(f"Non-dict passed to WandbHandler {e} msg:{msg}")
