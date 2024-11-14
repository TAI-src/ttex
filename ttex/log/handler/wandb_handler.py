import logging
from typing import Dict
import wandb

class WandbHandler(logging.Handler):
    """
    Handler that will emit results to wandb
    """
    def __init__(self, wandb_args: Dict, level=logging.NOTSET):
        super().__init__(level)
        self.wandb_args = wandb_args
        
        assert "project" in wandb_args
        assert "config" in wandb_args

        self.run = wandb.init(
            # Set the project where this run will be logged
            project=wandb_args["project"],
            # Track hyperparameters and run metadata
            config=wandb_args["config"],
        )

    def emit(self,record):
        msg = record.getMessage()
        if isinstance(msg, dict):
            wandb.log(msg)
