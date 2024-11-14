import logging
from ttex.log.handler import WandbHandler
import os
import pkg_resources
import shutil

def test_wandb_handler():
    prev_mode = os.environ.get("WANDB_MODE", "online")
    os.environ["WANDB_MODE"] = "offline"
    ttex_version = pkg_resources.require("tai_ttex")[0].version
    wandb_args = {
        "project": "ci-cd",
        "config": {"repo": "ttex",
                   "version": ttex_version}
    }
    handler = WandbHandler(wandb_args)
    logger = logging.getLogger("test_wandb_handler")
    logger.setLevel(logging.DEBUG)

    logger.addHandler(handler)
    logger.info("test")
    os.environ["WANDB_MODE"] = prev_mode

    shutil.rmtree(handler.run.dir)
