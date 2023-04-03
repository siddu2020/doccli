# DocCli

Python 3.10+ utility to build Classes that can be easily modified to create a Python
Argparse specification. The goal of this is to couple a CLI specification to a config
class, making them quicker to build and less likely to break.

This leans heavily on the [Decli](https://github.com/Woile/decli) library
to generate Argparse objects.

## Creating CLI Objects

CLI objects can be created automatically from a class definition, reading in default
values and descriptions from type hints and the docstring.

```python
from doccli import DocCliParser

class CliTool:
    command_name = "cli-tool"
    def __init__(self, _non_cli_param: str, param_a: str, param_b, param_c: int = 5):
        """This is the command description

        Args:
            _non_cli_param (str): Underscore leading params aren't included in the
                                  CLI specs
            param_a: A required parameter
            param_b: Note that the type needs to come from the annotation
            param_c: This one has a default
        """

        self.param_a = param_a
        self.param_b = param_b
        self.param_c = param_c

        self.non_cli_param = non_cli_param

# To create the argparse object:
if __name__ == "__main__":
    args = DocliParser(CliTool).parse_args()
    ...
```

See [examples](examples/) for more examples, including how to create CLIs with
[subcommands](examples/subcommands.py).

## Config File Helpers

DocCli also provides the `ConfigUtil` class which can be used to automatically
create Yaml config files. These include the ability to:

- Infer config specifications from the `__init__` method
- Convert an instantiated object into a dictionary
  - This will ignore config values that have the same value as their default
- Ability to nest Config objects in other objects, to create centralised config files
  - A sub-config object can still be instantiated from the super YAML file

Objects inheriting from the `ConfigUtil` class can set the following class level
variables:

- config_key: str
  - Parameters for this object. Defaults to the class name
- sub_config_list: List<ConfigUtil>
  - A list of Config Classes that also inherit from ConfigUtil, and are children of this class
- flatten_sub_configs: bool
  - Defaults to True. When reading from/writing to a dict, sub_configs will either be recorded
    as sub-dictionaries, or at the same level as the config items for the current dictionary.

## Using them together

These tools can be used together to create a config class that can:

- Generate a CLI parser
- Initiate from a CLI parser, while also filling in unsupplied values from a Config file
- Write supplied values to a config file so they can be remembered later

DocliParser has the method `parse_args_with_config_file`, which will attempt to
fill in any unprovided arguments with values provided in the Config File. Note that
this will only work if:

- The variables are stored as top-level keys in the file
- The variables are stored in a sub-dictionary under the same key as the subcommand name
- If the subcommand class inherits from `ConfigUtil` and the variables are stored in a
  sub-dictionary under the same key as the ConfigUtil.config_key variable

An example of this can be seen in [examples](examples/webserver_conf.py)
