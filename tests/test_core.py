import argparse
from doccli import DocliParser

from unittest import TestCase


class CliTool:
    def __init__(self, _non_cli_param: str, param_a: str, param_b, param_c: int = 5):
        """command-name

        This is the command description
        
        Args:
            _non_cli_param (str): Underscore leading params aren't included in the
                                  CLI specs
            param_a: A required parameter 
            param_b: Note that the type needs to come from the annotation
            param_c: This one has a default
        """

        self.param_a = param_a
        self.param_b = param_b

        self._non_cli_param = _non_cli_param


class SuperTool:
    """main-tool

    Main CLI class to route to subcommands
    """


class TestCore(TestCase):
    def test_basic_cli_tool(self):
        parser_spec = DocliParser.create_decli_spec(CliTool)

        self.assertDictEqual(
            parser_spec,
            {
                "prog": "command-name",
                "description": "This is the command description",
                "arguments": [
                    {"name": "--param-a", "type": str, "help": "A required parameter"},
                    {
                        "name": "--param-b",
                        "help": "Note that the type needs to come from the annotation",
                    },
                    {
                        "name": "--param-c",
                        "type": int,
                        "default": 5,
                        "help": "This one has a default",
                    },
                ],
            },
        )

    def test_create_parser(self):
        docliparser = DocliParser(CliTool)
        parser = docliparser.parser

        assert issubclass(parser.__class__, argparse.ArgumentParser)

    def test_subcommands(self):
        docliparser = DocliParser(SuperTool)
        docliparser.add_subcommand(CliTool, func=lambda **kwargs: len(kwargs))
        spec = docliparser.spec
        func = spec["subcommands"]["commands"][0].pop("func")
        self.assertDictEqual(
            docliparser.spec,
            {
                "prog": "main-tool",
                "description": "Main CLI class to route to subcommands",
                "subcommands": {
                    "title": "Positional Arguments",
                    "description": "Run main-tool <arg> --help for further details",
                    "commands": [
                        {
                            "arguments": [
                                {
                                    "name": "--param-a",
                                    "type": str,
                                    "help": "A required parameter",
                                },
                                {
                                    "name": "--param-b",
                                    "help": "Note that the type needs to come from the annotation",
                                },
                                {
                                    "name": "--param-c",
                                    "type": int,
                                    "default": 5,
                                    "help": "This one has a default",
                                },
                            ],
                            "name": "command-name",
                            "help": "This is the command description",
                        }
                    ],
                },
            },
        )

        spec["subcommands"]["commands"][0]["func"] = func

        parser = docliparser.parser
        assert issubclass(parser.__class__, argparse.ArgumentParser)

        res = parser.parse_args(
            ["command-name", "--param-a", "hey", "--param-b", "you", "--param-c", "2"]
        )

        assert res.param_a == "hey"
        assert res.param_b == "you"
        assert res.param_c == 2

        assert res.func(**vars(res)) == 4  # params + func 

