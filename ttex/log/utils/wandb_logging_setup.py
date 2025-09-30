import logging
from ttex.log.handler import WandbHandler
from typing import Optional, Dict, List
import wandb
from importlib.metadata import distributions
from wandb.sdk import AlertLevel
import os.path as osp
from dataclasses import dataclass
from ttex.log import capture_snapshot


def setup_wandb_logger(
    run: wandb.sdk.wandb_run.Run,
    custom_metrics: Optional[Dict] = None,
    name: str = "wandb_logger",
    level: int = logging.INFO,
) -> logging.Logger:
    logger = logging.getLogger(name)
    if not getattr(logger, "_wandb_setup", None):
        logger._wandb_setup = True  # type: ignore[attr-defined]

        logger.propagate = False  # Prevent double logging
        logger.setLevel(level)

        wandb_handler = WandbHandler(wandb_run=run, custom_metrics=custom_metrics)
        wandb_handler.setLevel(level)
        logger.addHandler(wandb_handler)
    return logger


@dataclass
class WandbArtifact:
    artifact_name: str
    local_path: str
    artifact_type: str = "evaluation"
    description: str = ""


@dataclass
class WandbSnapshot:
    extra_info: Optional[Dict] = None
    extra_sensitive_keys: Optional[List[str]] = None


def teardown_wandb_logger(
    run: wandb.sdk.wandb_run.Run,
    exit_code: int,
    artifacts: Optional[List[WandbArtifact]] = None,
    snapshot: Optional[WandbSnapshot] = None,
) -> None:
    artifacts = artifacts or []
    if snapshot:
        snapshot_path = f"snapshot_{run.id}.json"
        capture_snapshot(
            output_path=snapshot_path,
            extra_info=snapshot.extra_info,
            extra_sensitive_keys=snapshot.extra_sensitive_keys,
        )
        create_wandb_artifact(
            run,
            artifact_name="system_snapshot",
            local_path=snapshot_path,
            artifact_type="dataset",
            description="System snapshot captured at the end of the run",
        )

    for artifact in artifacts:
        create_wandb_artifact(
            run,
            artifact_name=artifact.artifact_name,
            local_path=artifact.local_path,
            artifact_type=artifact.artifact_type,
            description=artifact.description,
        )

    if exit_code == 0:
        run.alert(
            title=f"Run {run.id} finished successfully",
            text="The run has completed without errors.",
            level=AlertLevel.INFO,
        )
    else:
        run.alert(
            title=f"Run {run.id} finished with errors",
            text="The run has completed with errors. Please check the logs for details.",
            level=AlertLevel.ERROR,
        )
    run.finish()


def create_wandb_artifact(
    run: wandb.sdk.wandb_run.Run,
    artifact_name: str,
    local_path: str,
    artifact_type: str = "evaluation",
    description: Optional[str] = "",
) -> wandb.sdk.wandb_artifact.Artifact:
    artifact_name = f"{artifact_name}_{run.id}"
    artifact = wandb.Artifact(
        name=artifact_name, type=artifact_type, description=description
    )
    if osp.exists(local_path):
        artifact.add_file(local_path=local_path, name=artifact_name)
    elif osp.isdir(local_path):
        artifact.add_dir(local_path=local_path, name=artifact_name)
    else:
        run.alert(
            title="Artifact Logging Error",
            text=f"Path {local_path} does not exist. Cannot log artifact {artifact_name}.",
            level=AlertLevel.WARNING,
        )
        return None
    run.log_artifact(artifact)
    return artifact


def wandb_init(
    run_config: Dict, project: Optional[str] = None, group: Optional[str] = None
):
    """
    Initialize wandb run
    Args:
        run_config (Dict): Run configuration
        project (Optional[str], optional): Wandb project. Defaults to None.
        group (Optional[str], optional): Wandb group. Defaults to None.
    Returns:
        wandb.sdk.wandb_run.Run: Wandb run
    """
    # log versions of all packages
    packages = {
        "pkg": {dist.metadata["Name"]: dist.version for dist in distributions()},
        "repo": "jaix",
    }

    run_config.update(packages)
    if not project:
        run = wandb.init(config=run_config, group=group)
    else:
        run = wandb.init(config=run_config, project=project, group=group)
    return run
