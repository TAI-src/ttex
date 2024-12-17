import logging
import ast
from wandb.sdk.wandb_run import Run

logger = logging.getLogger()


class WandbHandler(logging.Handler):
    """
    Handler that will emit results to wandb
    """

    def __init__(self, wandb_run: Run, level=logging.NOTSET):
        super().__init__(level)
        self.run = wandb_run

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
