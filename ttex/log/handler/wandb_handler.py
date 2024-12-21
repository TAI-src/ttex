import logging
import ast
from wandb.sdk.wandb_run import Run
from typing import Optional, Dict
from ttex.log import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class WandbHandler(logging.Handler):
    """
    Custom logging handler to log to wandb
    """

    def __init__(
        self,
        wandb_run: Run,
        custom_metrics: Optional[Dict] = None,
        level=logging.NOTSET,
    ):
        """
        Args:
            wandb_run (Run): Wandb run object
            custom_metrics (Optional[Dict], optional): Custom metrics to define. Defaults to None.
            level ([type], optional): Logging level. Defaults to logging.NOTSET.
        """
        super().__init__(level)
        self.run = wandb_run
        if custom_metrics:
            for step_metric, metrics in custom_metrics.items():
                self.run.define_metric(step_metric)
                for metric in metrics:
                    self.run.define_metric(metric, step_metric=step_metric)

    def emit(self, record):
        """
        Emit the record to wandb
        Args:
            record (LogRecord): Log record
        """
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
