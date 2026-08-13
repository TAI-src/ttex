from ttex.log.filter.event.environment_events import EnvironmentStep
from ttex.log.filter.tracker.parser import Parser
import numpy as np


def test_parser_retrieve_val():
    parser = Parser()
    event = EnvironmentStep(
        observation=np.array([10, 20, 30]),
        reward=0.0,
        trunc=False,
        term=True,
        info={"key1": {"key2": 42}, "key3": 100, "key4": [1, 2, 3]},
    )
    assert parser.retrieve_val(event, "info.key1.key2") == 42
    assert parser.retrieve_val(event, "info.key3") == 100
    assert parser.retrieve_val(event, "info.key4") == [1, 2, 3]
    assert parser.retrieve_val(event, "info.key5") is None
    assert parser.retrieve_val(event, "info.key4.0") == 1
    assert parser.retrieve_val(event, "info.key1") == {"key2": 42}

    assert np.array_equal(
        parser.retrieve_val(event, "observation"), np.array([10, 20, 30])
    )
    assert parser.retrieve_val(event, "observation.2") == 30
    assert parser.retrieve_val(event, "observation.3") is None

    assert parser.retrieve_val(event, "reward") == 0.0
    assert parser.retrieve_val(event, "trunc") is False
    assert parser.retrieve_val(event, "term") is True

    assert parser.retrieve_val(event, "nonexistent") is None
    assert parser.retrieve_val(event, "info.key1.key2.nonexistent") is None
    assert parser.retrieve_val(event, "info.key4.10") is None
    assert parser.retrieve_val(event, "obs.0") is None
