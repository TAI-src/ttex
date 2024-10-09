""" Config class and ConfigFactory to create one from different sources"""

from abc import ABC
from typing import TypeVar, Type
from inspect import signature, Parameter


# TODO config with separate levels for keys
class Config(ABC):  # pylint: disable=too-few-public-methods
    """Config to go with a configurable object

    Contains the necessary values required to initialise a configurable object
     as defined by that object's specific config
    """

    def __init__(self, *args, **kwargs):
        """Init a configuration
        Should be overriden by each Config object to specify
        exactly which values are required
        """
        # TODO could add something that auto-adds all the values to the dict
        # TODO consider if this should be a dictionary or a namedtuple or sth

    def get_val(self, key: str, default=None):
        """Get a specific value from the config dict.
        This might need to be modified for nesting
        Ideally also shouldn't access the dict directly
        """
        return self.__dict__.get(key, default)


T = TypeVar("T", bound=Config)


class ConfigFactory(ABC):
    """Provides different convenience methods to create a Config Object"""

    @staticmethod
    def _extract_default(param: Parameter):
        """Extract fefault value from a parameter

        If it has a default, return that - else return None

        Args:
            param (Parameter): The parameter from which the default values
            are to be extracted

        Returns:
            param.default (?): The default value if it exists. Else None

        """
        return param.default if param.default != Parameter.empty else None

    @staticmethod
    def extract(config_class: Type[T], config: Config) -> T:
        """Extract Config of config_class from config

        Creates an object of type config_class
         by extracting the relevant values from the config

        Args:
            config_class (Type[T: Config]): They type of config being created
            config (Config): The config containing the values to be extracted

        Returns:
            sub_config (T:Config): the extracted config of type config_class

        """
        signa = signature(config_class.__init__)
        values = {
            p.name: config.get_val(p.name, ConfigFactory._extract_default(p))
            for _, p in signa.parameters.items()
            if p.name != "self"
        }
        return config_class(**values)

    @staticmethod
    def from_dict(dict_config: dict) -> Config:
        """Create config from a dict

        Creates a config by reading the dict and extracting each sub-config.
        Needs to be in a specific format

        Args:
            dict_config (dict): Dict containing the values to put into config

        Returns:
            config (Config): the extracted Config

        """
        # TODO describe format
        # TODO figure out how exactly this is going to work with the extraction
        # - do all values need to be unique? What do about paths inside config
        raise NotImplementedError()

    @staticmethod
    def from_file(path_to_json_file: str) -> Config:
        """Create config from a json file

        Creates a config by reading the json file + extracting each sub-config.
        Needs to be in a specific format
        #TODO describe format


        Args:
            path_to_json_file (str): Path to json file containing
                                     the values to be put into the config

        Returns:
            config (Config): the extracted Config

        """
        # TODO read in json file
        # TODO json file needs to be able to do paths to other configs: nested
        # dict_config = {}
        # return ConfigFactory.from_dict(dict_config)
        raise NotImplementedError()
