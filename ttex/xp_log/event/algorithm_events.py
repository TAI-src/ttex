from dataclasses import dataclass, field
from uuid import uuid4

from ttex.xp_log.event.experiment_events import (
    ClosingEvent,
    ConfigEvent,
    ExperimentEvent,
)


@dataclass(frozen=True, kw_only=True)
class AlgorithmEvent(ExperimentEvent):
    """
    Base class for all algorithm-related events.
    """

    exp_id: str | None = (
        None  # Experiment ID, should match the one from ExperimentStart
    )
    algo_state: (
        dict  # Current state of the algorithm (e.g., parameters, internal variables)
    )


@dataclass(frozen=True, kw_only=True)
class AlgorithmStart(AlgorithmEvent, ConfigEvent):
    """
    Event representing the initialization of an algorithm within an experiment.
    """

    id: str = field(
        default_factory=lambda: str(uuid4())
    )  # Unique ID for the event, defaults to a random UUID


@dataclass(frozen=True, kw_only=True)
class TrainingStart(AlgorithmEvent):
    """
    Event representing the start of training for an algorithm within an experiment.
    """


@dataclass(frozen=True, kw_only=True)
class TrainingEnd(AlgorithmEvent):
    """
    Event representing the end of training for an algorithm within an experiment.
    """


@dataclass(frozen=True, kw_only=True)
class EvaluationStart(AlgorithmEvent):
    """
    Event representing the start of evaluation for an algorithm within an experiment.
    """


@dataclass(frozen=True, kw_only=True)
class EvaluationEnd(AlgorithmEvent):
    """
    Event representing the end of evaluation for an algorithm within an experiment.
    """


@dataclass(frozen=True, kw_only=True)
class AlgorithmStop(AlgorithmEvent, ClosingEvent):
    """
    Event representing the closing of an algorithm within an experiment.
    """


@dataclass(frozen=True, kw_only=True)
class AlgorithmAction(AlgorithmEvent):
    """
    Event representing a step taken by the algorithm.
    """

    action: dict  # Action taken by the algorithm


@dataclass(frozen=True, kw_only=True)
class AlgorithmRestart(AlgorithmEvent):
    """
    Event representing the restart of an algorithm within an experiment.
    """
