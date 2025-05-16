# Config

This module implements convenience features for making classes configurable with json files, including [input sanitization](#configuration-sanitization). To make any class configurable, it should look roughly like this:

```python
from ttex.config import ConfigurableObject, Config

class MyClassConfig(Config):
    def __init__(self, property1: str, property2: int):
        # Save the properties
        self.property1 = property1
        self.property2 = property2

class MyClass(ConfigurableObject):
    config_class = MyClassConfig

    def __init__(self, config: MyClassConfig, ...):
        ConfigurableObject.__init__(self, config) # Not always necessary, but good practice
        # Initialize your class here
        # All properties in the config are now accessible
        # via self.property1, self.property2, etc.

  # Rest of the class
```

The corresponding config file would look like this:

```json
{
  "full.path.to.MyClassConfig": {
    "property1": "val1",
    "property2": 0
  }
```

## Supported property types

The following property basic types are supported (and tested) in the config:
- Text Type: `str`
- Numeric Types: `int`, `float`
- Boolean Type: `bool`
- Sequence Types: `list`, `tuple`
- Mapping Types: `dict`
- None Type: `NoneType`

Beyond the above, it is also possible to use fully custom types. This works out-of-the-box if no serialization is required. If JSON serialization is required, there are a few extra considerations:

- [Config](/ttex/config/config.py): If the type is a Config object, it should be serialized as a dict. For more details, see [Nested Configs](#nested-configs) below.
- Enum Types: If the type is an Enum, it should be serialized as a string ("MyEnum.MyOption"). The enum class must be imported (available in `globals()`), or the full path needs to be provided.
- Custom Classes: Any class can be passed as a string. If it is available in `globals()` or can be imported (full path given), it will be converted from string to that class.
- [ConfigurableObject](/ttex/config/configurable_object.py): Configurable objects should not be passed directly, but instead the `Config` and `ConfigurableObject` class should be passed separately. Refer to section on [configurable objects](#configurable-objects) for more details.

For an example, check out the [config](/test/config/__init__.py) used in testing.



### Nested Configs
It is also possible to nest configs. So if one of the properties in `MyClassConfig` is another config that inherits from `Config`, the json config could look like this:

```json
{
  "full.path.to.MyClassConfig": {
    "property1": "val1",
    "property2": 0,
    "nested_property": {
      "full.path.to.NestedClassConfig": {
        "nested_property1": "val1",
        "nested_property2": 0
      }
    }
  }
}
```

### Configurable objects

In order to serialize objects, they need to inherit from `ConfigurableObject`. So let's extend the example from above accordingly:

```python
from ttex.config import ConfigurableObject, Config, ConfigurableObjectFactory as COF
from typing import Type
from above import MyClassConfig, MyClass # See example above

class MyClass2Config(Config):
    def __init__(self, property1: str, property2: int,
                 conf_obj_class: Type[ConfigurableObject],
                 conf_obj_config: Config):
        # Save the properties
        self.property1 = property1
        self.property2 = property2
        self.conf_obj_class = conf_obj_class
        self.conf_obj_config = conf_obj_config

class MyClass2(ConfigurableObject):
    config_class = MyClass2Config

    def __init__(self, config: MyClassConfig, ...):
        ConfigurableObject.__init__(self, config) # Not always necessary, but good practice
        conf_obj = COF.create(config.conf_obj_class, config.conf_obj_config)

  # Rest of the class
```

The corresponding config file would look like this:

```json
{
  "full.path.to.MyClass2Config": {
    "property1": "val1.1",
    "property2": 2,
    "conf_obj_class": "full.path.to.MyClass",
    "conf_obj_config": {
      "full.path.to.MyClassConfig": {
        "property1": "val1",
        "property2": 0
      }
    }
  }
```

## Configuration Sanitization

If the built-in factory classes are used for object instantiation, the provided configs are sanitized automatically. So a `ConfigurableObject` should always be created using the [ConfigurableObjectFactory (COF)](/ttex/config/configurable_object.py).
```python
from ttex.config import ConfigurableObjectFactory as COF

conf_obj = COF.create(conf_obj_class, conf_obj_config)
```

The config can be passed as any of the following types:
- `Config`: A config object that inherits from `Config`.
- dict: A dictionary that contains the config properties. The keys should be the property names and the values should be the corresponding values.
- str: A string that contains the path to the config file. The config file should be in JSON format and should contain the config properties.

Internally, the [`ConfigFactory`](/ttex/config/config.py) takes care of parsing the input and creating the config object. It also checks that all required values are provided and no additional, unexpected properties are passed. The `COF` then takes care of initialising the `ConfigurableObject` with the created `Config` object.

## Examples


More extensive examples (beyond what is found in the tests) can be seen in the `jaix` project. See for example:

- [Sphere](https://github.com/TAI-src/jaix/blob/main/jaix/env/utils/problem/sphere.py): Simple class with a config of mostly basic types plus lists. 
- [SwitchingEnvironment](https://github.com/TAI-src/jaix/blob/main/jaix/env/composite/switching_environment.py): More complex class, which (among other things), initialises a `SwitchingPattern`, which is a `ConfigurableObject`
- [Example Json Configurations](https://github.com/TAI-src/jaix/tree/main/experiments)
