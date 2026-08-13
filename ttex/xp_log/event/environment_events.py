from dataclasses import dataclass, field
from uuid import uuid4

from ttex.xp_log.event.experiment_events import (
    ClosingEvent,
    ConfigEvent,
    ExperimentEvent,
)


@dataclass(frozen=True, kw_only=True)
class EnvironmentEvent(ExperimentEvent):
    """
    Base class for all environment-related events.
    """

    exp_id: str | None = (
        None  # Experiment ID, should match the one from ExperimentStart
    )
    alg_id: str | None = None  # Algorithm ID, should match the one from AlgorithmInit


@dataclass(frozen=True, kw_only=True)
class EnvironmentInit(EnvironmentEvent, ConfigEvent):
    """
    Event representing the start of an environment within an experiment.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )  # Unique ID for the event, defaults to a random UUID


@dataclass(frozen=True, kw_only=True)
class EnvironmentClose(EnvironmentEvent, ClosingEvent):
    """
    Event representing the closing of an environment within an experiment.
    """


@dataclass(frozen=True, kw_only=True)
class EnvironmentStep(EnvironmentEvent):
    """
    Event representing a step taken in the environment.
    """

    observation: dict  # Observation from the environment
    reward: float  # Reward received from the environment
    trunc: bool  # Whether the episode has been truncated
    term: bool  # Whether the episode has terminated
    info: dict  # Additional information from the environment


@dataclass(frozen=True)
class EnvironmentReset(EnvironmentEvent):
    """
    Event representing the reset of the environment.
    """

    observation: dict  # Initial observation after reset
    seed: int | None = None  # Optional seed used for the reset
