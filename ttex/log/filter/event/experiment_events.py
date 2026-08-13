from dataclasses import dataclass, field
from uuid import uuid4

from ttex.config import Config
from ttex.log.filter.event_keysplit_filter import LogEvent


@dataclass(frozen=True, kw_only=True)
class ExperimentEvent(LogEvent):
    """
    Base class for all experiment-related events.
    """

    id: str | None = None  # Experiment ID, should match the one from ExperimentStart


@dataclass(frozen=True, kw_only=True)
class ClosingEvent(LogEvent):
    """
    Base class for all closing events.
    """

    artifacts: dict[str, str] | None = (
        None  # Dictionary of artifact names to file paths
    )


@dataclass(frozen=True, kw_only=True)
class ConfigEvent(LogEvent):
    """
    Base class for all configuration events.
    """

    config: Config | dict  # Configuration object or dictionary
    kwargs: dict  # Additional runtime args for the init


@dataclass(frozen=True, kw_only=True)
class ExperimentStart(ExperimentEvent, ConfigEvent):
    """
    Event representing the start of an experiment.
    Experiments are assumed to run a single algorithm on a set of environments, and can have multiple phases (e.g., offline, online, post).
    If multiple algorithms are run, separate experiments should be started for each algorithm.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )  # Unique ID for the event, defaults to a random UUID


@dataclass(frozen=True, kw_only=True)
class ExperimentEnd(ExperimentEvent, ClosingEvent):
    """
    Event representing the end of an experiment.
    """
