from ttex.config import Config, ConfigFactory
from . import DummyConfig


def test_get_val():
    config = Config()
    config.test = 5

    assert config.get_val("test") == 5
    assert config.get_val("test2") is None

    # default values
    assert config.get_val("test", 3) == 5
    assert config.get_val("test2", 3) == 3


def test_extract_empty():
    config = Config()
    test_config = ConfigFactory.extract(DummyConfig, config)
    assert test_config.a is None
    assert test_config.b is None
    assert test_config.c is None
    assert test_config.d == 3


def test_extract():
    config = Config()
    config.a = "arg"
    config.b = 5
    config.c = "kwarg"
    config.d = 17

    test_config = ConfigFactory.extract(DummyConfig, config)

    for arg in ["a", "b", "c", "d"]:
        assert getattr(test_config, arg) == getattr(config, arg)
