import os
import shutil
from copy import deepcopy
from ttex.log.utils.wandb_logging_setup import (
    wandb_init,
    setup_wandb_logger,
    teardown_wandb_logger,
    WandbArtifact,
    WandbSnapshot,
)
import logging


def test_wandb_init():
    prev_mode = os.environ.get("WANDB_MODE", "online")
    os.environ["WANDB_MODE"] = "offline"
    run = wandb_init(run_config={"dummy": "test_wandb_init"}, project="ci-cd")
    assert run.settings.run_mode == "offline-run"
    shutil.rmtree(run.dir, ignore_errors=True)
    run.finish()

    os.environ["WANDB_MODE"] = prev_mode


def test_setup_wandb_logger():
    prev_mode = os.environ.get("WANDB_MODE", "online")
    os.environ["WANDB_MODE"] = "offline"
    run = wandb_init(run_config={"dummy": "test_setup_wandb_logger"}, project="ci-cd")
    logger = setup_wandb_logger(run=run, name="test_wandb_logger", level=logging.INFO)
    assert logger.name == "test_wandb_logger"
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers) == False
    shutil.rmtree(run.dir, ignore_errors=True)
    run.finish()
    os.environ["WANDB_MODE"] = prev_mode
