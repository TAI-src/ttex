from dataclasses import dataclass, field
from uuid import uuid4
from ttex.config import Config

from ttex.log.filter.event_keysplit_filter import LogEvent


@dataclass(frozen=True, kw_only=True)
class ExperimentEvent(LogEvent):
    """
    Base class for all experiment-related events.
    """

    exp_id: str | None = (
        None  # Experiment ID, should match the one from ExperimentStart
    )


@dataclass(frozen=True, kw_only=True)
class ClosingEvent(LogEvent):
    """
    Base class for all closing events.
    """

    artifacts: dict[str, str] | None = (
        None  # Dictionary of artifact names to file paths
    )


@dataclass(frozen=True, kw_only=True)
class ExperimentStart(ExperimentEvent):
    """
    Event representing the start of an experiment.
    Experiments are assumed to run a single algorithm on a set of environments, and can have multiple phases (e.g., offline, online, post).
    If multiple algorithms are run, separate experiments should be started for each algorithm.
    """

    exp_config: (
        Config | dict
    )  # Experiment configuration, can be a Config object or a dictionary
    exp_kwargs: dict  # Additional runtime args for the experiment
    exp_id: str = field(
        default_factory=lambda: str(uuid4())
    )  # Experiment ID, defaults to a random UUID


@dataclass(frozen=True, kw_only=True)
class ExperimentEnd(ExperimentEvent, ClosingEvent):
    """
    Event representing the end of an experiment.
    """

    pass


@dataclass(frozen=True, kw_only=True)
class EnvironmentEvent(ExperimentEvent):
    """
    Base class for all environment-related events.
    """

    env_id: str | None = (
        None  # Environment ID, should match the one from EnvironmentInit
    )


@dataclass(frozen=True, kw_only=True)
class EnvironmentInit(EnvironmentEvent):
    """
    Event representing the start of an environment within an experiment.
    """

    env_config: (
        Config | dict
    )  # Environment configuration, can be a Config object or a dictionary
    env_kwargs: dict  # Additional runtime args for the environment
    phase: str = "online"  # Phase of the experiment (e.g., "offline", "online", "post")
    env_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )  # Environment ID, defaults to a random UUID
    )


@dataclass(frozen=True, kw_only=True)
class EnvironmentClose(EnvironmentEvent, ClosingEvent):
    """
    Event representing the closing of an environment within an experiment.
    """

    pass


@dataclass(frozen=True, kw_only=True)
class EnvironmentStep(EnvironmentEvent):
    """
    Event representing a step taken in the environment.
    """

    step: int  # Current step number
    observation: dict  # Observation from the environment
    reward: float  # Reward received from the environment
    done: bool  # Whether the episode has ended
    info: dict  # Additional information from the environment


@dataclass(frozen=True)
class EnvironmentReset(EnvironmentEvent):
    """
    Event representing the reset of the environment.
    """

    observation: dict  # Initial observation after reset
    seed: int | None = None  # Optional seed used for the reset


@dataclass(frozen=True, kw_only=True)
class AlgorithmEvent(EnvironmentEvent):
    """
    Base class for all algorithm-related events.
    """

    algo_id: str | None = None  # Algorithm ID, should match the one from AlgorithmInit


@dataclass(frozen=True, kw_only=True)
class AlgorithmStart(AlgorithmEvent):
    """
    Event representing the initialization of an algorithm within an experiment.
    """

    algo_config: (
        Config | dict
    )  # Algorithm configuration, can be a Config object or a dictionary
    algo_kwargs: dict  # Additional runtime args for the algorithm
    algo_id: str = field(
        default_factory=lambda: str(uuid4())
    )  # Algorithm ID, defaults to a random UUID


@dataclass(frozen=True, kw_only=True)
class AlgorithmStop(AlgorithmEvent, ClosingEvent):
    """
    Event representing the closing of an algorithm within an experiment.
    """

    pass


@dataclass(frozen=True, kw_only=True)
class AlgorithmStep(AlgorithmEvent):
    """
    Event representing a step taken by the algorithm.
    """

    step: int  # Current step number
    action: dict  # Action taken by the algorithm
    algo_state: (
        dict  # Current state of the algorithm (e.g., parameters, internal variables)
    )
