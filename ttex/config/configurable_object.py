from abc import ABC
from typing import TypeVar, Type
import logging

from ttex.config.config import Config, ConfigFactory

logger = logging.getLogger("DefaultLogger")


class ConfigurableObject(ABC):  # pylint: disable=too-few-public-methods
    config_class = Config

    def __init__(self, config: Config, *args, **kwargs):
        self.config = config
        if not isinstance(config, self.config_class):
            logger.warning(
                "Config type does not align. Given config was %s"
                + " but given config_class was %s",
                type(config),
                self.config_class,
            )
        self.apply_config(self.config)

    def apply_config(self, config):
        self.__dict__.update(config.__dict__)


T = TypeVar("T", bound=ConfigurableObject)


class ConfigurableObjectFactory(ABC):  # pylint: disable=too-few-public-methods
    """Utility to create a Configurable Object"""

    @staticmethod
    def create(
        configurable_object_class: Type[T], config: Config, *args, **kwargs
    ) -> T:
        """Create configurable object with the given config

         Args:
            configurable_object_class (Type[T: ConfigurableObject]):
                 They type of configurable object being created
            config (Config): The config for the object

        Returns:
            configurable object (T:Configurable object):
                the configured configurable object
        """

        # TODO should try force-casting
        if not isinstance(config, configurable_object_class.config_class):
            logger.warning(
                "Config type does not align. Given config was %s"
                + " but given config_class was %s",
                type(config),
                configurable_object_class.config_class,
            )
        typed_config = ConfigFactory.extract(
            configurable_object_class.config_class, config
        )
        return configurable_object_class(typed_config, *args, **kwargs)
