from ttex.config import (
    ConfigurableObject,
    ConfigurableObjectFactory,
)
from . import DummyConfig, EmptyConfig
from .. import dummy_log_handler


class DummyConfigurableObject(ConfigurableObject):
    config_class = DummyConfig

    def __init__(self, config: DummyConfig, args_test, kwargs_test=None):
        self.args_test = args_test
        self.kwargs_test = kwargs_test
        super().__init__(config)


def test_configurable_object():
    config = DummyConfig(a=1, b=2, c=3, d=5)
    conf_obj = DummyConfigurableObject(config, "test")

    # init
    assert conf_obj.config_class == type(config)

    # apply config
    for arg in ["a", "b", "c", "d"]:
        assert getattr(conf_obj, arg) == getattr(config, arg)


def test_wrong_config_class():
    config = EmptyConfig()
    dummy_log_handler.last_record = None
    conf_obj = DummyConfigurableObject(config, "test")
    # assert that the wrong type has been picked up
    assert dummy_log_handler.last_record is not None
    assert conf_obj.config_class == DummyConfig
    assert isinstance(conf_obj.config, EmptyConfig)


def test_create():
    config = DummyConfig(a=1, b=2, c=3, d=5)
    conf_obj = ConfigurableObjectFactory.create(
        DummyConfigurableObject, config, "test", kwargs_test="kwargs_test"
    )

    assert isinstance(conf_obj, DummyConfigurableObject)
    # apply config
    for arg in ["a", "b", "c", "d"]:
        assert getattr(conf_obj, arg) == getattr(config, arg)
    assert getattr(conf_obj, "args_test") == "test"
    assert getattr(conf_obj, "kwargs_test") == "kwargs_test"
