import argparse
import os
from unittest import TestCase

from doccli import DocCliParser, ConfigUtil


class CliTool:
    command_name = "cli"

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

        self._non_cli_param = _non_cli_param


class SuperTool:
    """Main CLI class to route to subcommands
    """

    command_name = "main-tool"


class TestCliParse(TestCase):
    def test_basic_cli_tool(self):
        parser_spec = DocCliParser.create_decli_spec(CliTool)

        self.assertDictEqual(
            parser_spec,
            {
                "prog": "cli",
                "description": "This is the command description",
                "arguments": [
                    {
                        "name": "--param-a",
                        "required": True,
                        "type": str,
                        "help": "A required parameter",
                    },
                    {
                        "name": "--param-b",
                        "required": True,
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
        docliparser = DocCliParser(CliTool)
        parser = docliparser.parser

        assert issubclass(parser.__class__, argparse.ArgumentParser)

    def test_subcommands(self):
        docliparser = DocCliParser(SuperTool)
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
                                    "required": True,
                                },
                                {
                                    "name": "--param-b",
                                    "help": "Note that the type needs to come from the annotation",
                                    "required": True,
                                },
                                {
                                    "name": "--param-c",
                                    "type": int,
                                    "default": 5,
                                    "help": "This one has a default",
                                },
                            ],
                            "name": "cli",
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
            ["cli", "--param-a", "hey", "--param-b", "you", "--param-c", "2"]
        )

        assert res.param_a == "hey"
        assert res.param_b == "you"
        assert res.param_c == 2

        assert res.func(**vars(res)) == 4  # params + func


test_file = "testfile.yml"


class ConfigCmd(ConfigUtil):
    command_name = "cfg"
    config_key = "config-cmd.options"

    def __init__(self, param_a: str, param_b: str):
        """This is the command description
        
        Args:
            param_a: A required parameter 
            param_b: Note that the type needs to come from the annotation
        """

        self.param_a = param_a
        self.param_b = param_b


class MainFunc(ConfigUtil):
    """Main CLI class to route to subcommands
    """

    sub_config_list = [ConfigCmd]
    config_key = "main"
    flatten_sub_commands = True


class TestParseWithFile(TestCase):
    def tearDown(self):
        try:
            os.remove(test_file)
        except FileNotFoundError:
            pass
        return super().tearDown()

    def test_parse_with_file(self):
        parser = DocCliParser(MainFunc)
        parser.add_subcommand(ConfigCmd)

        parser.parse_args(["cfg", "--param-a", "hey", "--param-b", "there"])

        # If we have a missing param then it will fail (loudly)
        with self.assertRaises(SystemExit):
            parser.parse_args(["cfg", "--param-a", "hey"])

        # We can solve this by including a missing variable in a config file
        cfg = MainFunc.with_config_dict(
            {"config-cmd.options": {"param_a": "new values", "param_b": "see"}}
        )
        cfg.to_config_file(test_file)

        args = parser._parse_args_with_config_file(
            ["cfg", "--param-a", "hey"], test_file
        )
        # Note that CLI takes precedence over config file with param a
        assert args == ["cfg", "--param-b", "see", "--param-a", "hey"]
