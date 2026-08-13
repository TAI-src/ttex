from ttex.config import Config
import pytest
from ttex.xp_log.event.experiment_events import (
    ConfigEvent,
    ExperimentStart,
    ExperimentEnd,
    ClosingEvent,
    ExperimentEvent,
)


@pytest.mark.parametrize(
    "config",
    [
        Config(param1="value1", param2=42),
        {"param1": "value1", "param2": 42},
    ],
)
def test_config_event_dict(config):
    kwargs = {"arg1": "valueA", "arg2": 3.14}
    event = ConfigEvent(config=config, kwargs=kwargs)

    assert event.config == config
    assert event.kwargs == kwargs


def test_exp_start():
    config = Config(param1="value1", param2=42)
    kwargs = {"arg1": "valueA", "arg2": 3.14}
    exp_start = ExperimentStart(config=config, kwargs=kwargs)

    assert isinstance(exp_start, ExperimentEvent)
    assert isinstance(exp_start, ConfigEvent)
    assert exp_start.config == config
    assert exp_start.kwargs == kwargs
    assert isinstance(exp_start.id, str) and len(exp_start.id) > 0


def test_exp_end():
    exp_end = ExperimentEnd(id="test_exp_id", artifacts={"model": "/path/to/model.pt"})

    assert isinstance(exp_end, ExperimentEvent)
    assert isinstance(exp_end, ClosingEvent)
    assert exp_end.id == "test_exp_id"
    assert exp_end.artifacts == {"model": "/path/to/model.pt"}
