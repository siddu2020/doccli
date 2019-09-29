# DocCli

Python 3.6+ utility to build Classes that can be easily modified to create a Python
Argparse specification. The goal of this is to couple a CLI specification to a config 
class, making them quicker to build and less likely to break.

This leans heavily on the [Decli](https://github.com/Woile/decli) library 
to generate Argparse specifications.

```python
from doccli import DocliParser

class CliTool:
    def __init__(self, _non_cli_param: str, param_a: str, param_b: int = 5):
        """Some CLI Tool description. 

        Note that only the short description is included in the parser description
        
        Args:
            _non_cli_param (str): Underscore leading params aren't included in the
                                  CLI specs
            param_a (str): A required parameter 
            param_b (int, optional): This one has a default
        """

        self.param_a = param_a
        self.param_b = param_b

        self.non_cli_param = non_cli_param

# This creates a Decli Specification 
parser_spec = DocliParser.create_decli_spec(CliTool)

assert parser_spec == {
    "prog": "CliTool",
    "description": "Some CLI Tool description",
    "arguments": [
        {
            "name": "--param-a",
            "type": str,
            "help": "A required parameter",
        },
        {
            "name": "--param-b",
            "type": int,
            "default": 5,
            "help": "This one has a default",
        },
    ],
}

# To create the argparse object:
parser = DocliParser(CliTool)
```

See [examples](examples/) for more examples.