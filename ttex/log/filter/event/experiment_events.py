from dataclasses import dataclass
from uuid import uuid4
from ttex.config import Config

from ttex.log.filter.event_keysplit_filter import LogEvent


@dataclass(frozen=True)
class ExperimentStart(LogEvent):
    """
    Event representing the start of an experiment.
    Experiments are assumed to run a single algorithm on a set of environments, and can have multiple phases (e.g., offline, online, post).
    If multiple algorithms are run, separate experiments should be started for each algorithm.
    """

    exp_config: (
        Config | dict
    )  # Experiment configuration, can be a Config object or a dictionary
    exp_kwargs: dict  # Additional runtime args for the experiment
    exp_id: str = str(uuid4())  # Experiment ID, defaults to a random UUID


@dataclass(frozen=True)
class ExperimentEnd(LogEvent):
    """
    Event representing the end of an experiment.
    """

    exp_id: str  # Experiment ID, should match the one from ExperimentStart


@dataclass(frozen=True)
class EnvironmentInit(LogEvent):
    """
    Event representing the start of an environment within an experiment.
    """

    env_config: (
        Config | dict
    )  # Environment configuration, can be a Config object or a dictionary
    env_kwargs: dict  # Additional runtime args for the environment
    exp_id: str  # Experiment ID, should match the one from ExperimentStart
    phase: str = "online"  # Phase of the experiment (e.g., "offline", "online", "post")
    env_id: str = str(uuid4())  # Environment ID, defaults to a random


@dataclass(frozen=True)
class EnvironmentClose(LogEvent):
    """
    Event representing the closing of an environment within an experiment.
    """

    env_id: str  # Environment ID, should match the one from EnvironmentStart


@dataclass(frozen=True)
class EnvironmentStep(LogEvent):
    """
    Event representing a step taken in the environment.
    """

    env_id: str  # Environment ID, should match the one from EnvironmentStart
    step: int  # Current step number
    observation: dict  # Observation from the environment
    reward: float  # Reward received from the environment
    done: bool  # Whether the episode has ended
    info: dict  # Additional information from the environment


@dataclass(frozen=True)
class EnvironmentReset(LogEvent):
    """
    Event representing the reset of the environment.
    """

    env_id: str  # Environment ID, should match the one from EnvironmentStart
    observation: dict  # Initial observation after reset


@dataclass(frozen=True)
class AlgorithmStart(LogEvent):
    """
    Event representing the initialization of an algorithm within an experiment.
    """

    algo_config: (
        Config | dict
    )  # Algorithm configuration, can be a Config object or a dictionary
    algo_kwargs: dict  # Additional runtime args for the algorithm
    exp_id: str  # Experiment ID, should match the one from ExperimentStart
    env_id: str  # Environment ID, should match the one from EnvironmentInit
    algo_id: str = str(uuid4())  # Algorithm ID, defaults to a random UUID


@dataclass(frozen=True)
class AlgorithmStop(LogEvent):
    """
    Event representing the closing of an algorithm within an experiment.
    """

    algo_id: str  # Algorithm ID, should match the one from AlgorithmInit
    env_id: str  # Environment ID, should match the one from EnvironmentInit


@dataclass(frozen=True)
class AlgorithmStep(LogEvent):
    """
    Event representing a step taken by the algorithm.
    """

    algo_id: str  # Algorithm ID, should match the one from AlgorithmInit
    env_id: str  # Environment ID, should match the one from EnvironmentInit
    step: int  # Current step number
    action: dict  # Action taken by the algorithm
    algo_state: (
        dict  # Current state of the algorithm (e.g., parameters, internal variables)
    )
