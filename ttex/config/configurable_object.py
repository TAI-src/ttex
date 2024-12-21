from abc import ABC
from typing import TypeVar, Type, Union, Dict, Optional
import logging
import os

from ttex.config.config import Config, ConfigFactory

logger = logging.getLogger("DefaultLogger")


class ConfigurableObject(ABC):  # pylint: disable=too-few-public-methods
    """
    Base class for objects that can be configured using a Config object.

    Attributes:
        config_class (Type[Config]): The class of the configuration object.
    """

    config_class = Config

    def __init__(self, config: Config, *args, **kwargs):
        """
        Initialize the ConfigurableObject with a given configuration.

        Args:
            config (Config): The configuration object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
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
        """
        Apply the configuration to the object.

        Args:
            config (Config): The configuration object.
        """
        self.__dict__.update(config.__dict__)


T = TypeVar("T", bound=ConfigurableObject)


class ConfigurableObjectFactory(ABC):  # pylint: disable=too-few-public-methods
    """
    Utility to create a Configurable Object.
    """

    @staticmethod
    def create(
        configurable_object_class: Type[T],
        config: Union[Dict, Config, str],
        *args,
        context: Optional[Dict] = None,
        **kwargs,
    ) -> T:
        """
        Create a configurable object with the given config.

        Args:
            configurable_object_class (Type[T]): The type of configurable object being created.
            config (Union[Dict, Config, str]): The config for the object. Can be passed directly as a config object,
                                               its dict representation, or as a file path to a JSON containing the dict.
            *args: Additional positional arguments.
            context (Optional[Dict]): Optional context for the configuration.
            **kwargs: Additional keyword arguments.

        Returns:
            T: The configured configurable object.
        """
        if isinstance(config, str):
            # Assuming this is a file path, load from file
            assert ".json" in config
            assert os.path.exists(config)
            config = ConfigFactory.from_file(config, context=context)

        if isinstance(config, dict):
            config = ConfigFactory.from_dict(config, context=context)

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
        logger.debug(f"Passed args {args} and kwargs {kwargs}")
        return configurable_object_class(typed_config, *args, **kwargs)
        if isinstance(config, str):
            # Assuming this is a file path, load from file
            assert ".json" in config
            assert os.path.exists(config)
            config = ConfigFactory.from_file(config, context=context)

        if isinstance(config, dict):
            config = ConfigFactory.from_dict(config, context=context)

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
        logger.debug(f"Passed args {args} and kwargs {kwargs}")
        return configurable_object_class(typed_config, *args, **kwargs)
        if isinstance(config, str):
            # Assuming this is a file path, load from file
            assert ".json" in config
            assert os.path.exists(config)
            config = ConfigFactory.from_file(config, context=context)

        if isinstance(config, dict):
            config = ConfigFactory.from_dict(config, context=context)

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
        logger.debug(f"Passed args {args} and kwargs {kwargs}")
        return configurable_object_class(typed_config, *args, **kwargs)
        if isinstance(config, str):
            # Assuming this is a file path, load from file
            assert ".json" in config
            assert os.path.exists(config)
            config = ConfigFactory.from_file(config, context=context)

        if isinstance(config, dict):
            config = ConfigFactory.from_dict(config, context=context)

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
        logger.debug(f"Passed args {args} and kwargs {kwargs}")
        return configurable_object_class(typed_config, *args, **kwargs)
