import logging
from ttex.log.handler import WandbHandler
from typing import Optional, Dict, List
import wandb
from importlib.metadata import distributions
from wandb.sdk import AlertLevel
import os.path as osp
from dataclasses import dataclass
from ttex.log import capture_snapshot
from ttex.log import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def setup_wandb_logger(
    custom_metrics: Optional[Dict] = None,
    name: str = "wandb_logger",
    level: int = logging.INFO,
) -> logging.Logger:
    wandb_logger = logging.getLogger(name)
    if not getattr(wandb_logger, "_wandb_setup", None):
        wandb_logger._wandb_setup = True  # type: ignore[attr-defined]

        wandb_logger.propagate = False  # Prevent double logging
        wandb_logger.setLevel(level)

        wandb_handler = WandbHandler(custom_metrics=custom_metrics)
        wandb_handler.setLevel(level)
        wandb_logger.addHandler(wandb_handler)
    return wandb_logger


def teardown_wandb_logger(name: str = "wandb_logger") -> None:
    wandb_logger = logging.getLogger(name)
    for handler in wandb_logger.handlers[:]:
        handler.close()
        wandb_logger.removeHandler(handler)
    wandb_logger._wandb_setup = False  # type: ignore[attr-defined]


def get_wandb_logger(name: str = "wandb_logger") -> Optional[logging.Logger]:
    wandb_logger = logging.getLogger(name)
    if not getattr(wandb_logger, "_wandb_setup", None):
        return None
    else:
        return wandb_logger


def get_wandb_handler(name: str = "wandb_logger") -> Optional[WandbHandler]:
    wandb_logger = get_wandb_logger(name=name)
    if wandb_logger is None:
        return None
    wandb_handler = next(
        (h for h in wandb_logger.handlers if isinstance(h, WandbHandler)), None
    )
    return wandb_handler


def log_wandb_init(
    run_config: Dict,
    project: Optional[str] = None,
    group: Optional[str] = None,
    logger_name: str = "wandb_logger",
) -> wandb.sdk.wandb_run.Run:
    handler = get_wandb_handler(name=logger_name)
    if handler is None:
        logger.warning("WandbHandler not found")
        return None
    run = WandbHandler.wandb_init(run_config=run_config, project=project, group=group)
    handler.run = run
    return handler.run


def log_wandb_artifact(
    logger_name: str,
    artifact_name: str,
    local_path: str,
    artifact_type: str = "evaluation",
    description: str = "",
) -> None:
    handler = get_wandb_handler(name=logger_name)
    if handler is None or not getattr(handler, "run", None):
        logger.warning("WandbHandler not found or not initialized with wandb run")
        return
    return handler.create_wandb_artifact(
        artifact_name=artifact_name,
        local_path=local_path,
        artifact_type=artifact_type,
        description=description,
    )
