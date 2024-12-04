from ttex.config import Config, ConfigFactory
from . import DummyConfig, dict_config
import pytest
from logging import Handler


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


def test_exctract_class():
    ex_class = ConfigFactory.extract_class("ttex.log.handler.WandbHandler")
    assert issubclass(ex_class, Handler)

    with pytest.raises(ValueError) as e:
        # Splitting error
        ConfigFactory.extract_class("DummyConfig")

    # Test error catching
    with pytest.raises(ValueError) as e:
        # Module import error
        ConfigFactory.extract_class("WandbHandler")
    assert "Did not recognise" in str(e.value)
    assert "KeyError" in str(e.value)

    with pytest.raises(ValueError) as e:
        # Module import error
        ConfigFactory.extract_class("tex.WandbHandler")
    assert "Did not recognise" in str(e.value)
    assert "No module named" in str(e.value)

    with pytest.raises(ValueError) as e:
        # class not found
        ConfigFactory.extract_class("ttex.WandbHandler")
    assert "Did not recognise" in str(e.value)
    assert "has no attribute" in str(e.value)


def test_from_dict():
    config = ConfigFactory.extract(
        DummyConfig, dict_config["DummyConfig"], context=globals()
    )
    assert isinstance(config, DummyConfig)
    assert config.a == "a"
    assert isinstance(config.b, DummyConfig)
    assert config.b.a == "a2"
    assert config.c == ConfigFactory
    print(config)
