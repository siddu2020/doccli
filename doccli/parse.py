import argparse
import copy
import inspect
import logging
import re
import sys
from typing import List, Dict, Type, TypeVar

import yaml
from decli import cli
from docstring_parser import parse

from . import ConfigUtil


class DocCliParser:
    def __init__(self, cls):
        """Generate a Cli object from a class's docstring and signature
        
        Args:
            cls (class): Class to render as cli
        """
        spec = self.create_decli_spec(cls)
        self.spec = spec

        self._mainkey = (
            self.spec["prog"] if not issubclass(cls, ConfigUtil) else cls.config_key
        )
        self._subcmd_config_map = {}

    @property
    def parser(self) -> argparse.ArgumentParser:
        return cli(self.spec)

    def parse_args(self, argv=None):
        return self.parser.parse_args(argv)

    @staticmethod
    def _check_dict_for_params(d: Dict, param_names: List[str]) -> List[str]:
        res = {}
        for param in param_names:
            param_key = (
                f"{param[2:].replace('-', '_')}" if param.startswith("--") else param
            )
            if param_key in d:
                res[param] = d[param_key]

        return res

    @staticmethod
    def _insert_params_into_argv(
        argv: List[str], index: int, available_params: Dict
    ) -> List[str]:
        for param, value in available_params.items():
            if param not in argv:
                argv.insert(index, param)
                argv.insert(index + 1, str(value))
        return argv

    def _parse_args_with_config_file(self, args: List[str], filename: str) -> List[str]:
        with open(filename, "r+") as f:
            contents = yaml.safe_load(f)

        # Add variables from Prog section
        params = [d["name"] for d in self.spec.get("arguments", dict())]
        config_params = ConfigUtil._get_sub_dict_by_key(self._mainkey, contents)
        if not config_params:
            config_params = contents
        else:
            config_params = config_params[self._mainkey]

        available_params = self._check_dict_for_params(config_params, params)
        args = self._insert_params_into_argv(args, 0, available_params)

        # Add subcommands
        for sub_cmd, config_name in self._subcmd_config_map.items():
            if sub_cmd in args:  # Get any unprovided args from the config file
                params = [
                    arg["name"]
                    for d in self.spec["subcommands"]["commands"]
                    for arg in d["arguments"]
                ]

                config_params = ConfigUtil._get_sub_dict_by_key(config_name, contents)
                if not config_params:
                    config_params = contents
                else:
                    config_params = config_params[config_name]

                available_params = self._check_dict_for_params(config_params, params)
                args = self._insert_params_into_argv(
                    args, args.index(sub_cmd) + 1, available_params
                )

        return args

    def parse_args_with_config_file(self, filename: str):
        """Adds any missing arguments for a given specification 
        from a YML config file. This assumes that positional 
        args are always located after keyword args
        
        Args:
            filename (str): Path to YML config file
        """
        args = copy.deepcopy(sys.argv[1:])
        args = self._parse_args_with_config_file(args, filename)
        return self.parser.parse_args(args)

    def add_subcommand(self, cls, func=None):
        """Parses a class and adds it as a subcommand
        
        Args:
            func: Default function used by argparse for this function
        """

        if not self.spec.get("subcommands"):
            self.spec["subcommands"] = {
                "title": "Positional Arguments",
                "description": f"Run {self.spec['prog']} <arg> --help for further details",
                "commands": [],
            }

        sub_spec = self.create_decli_spec(cls)
        sub_spec["name"] = sub_spec.pop("prog")
        sub_spec["help"] = sub_spec.pop("description")
        if func:
            sub_spec["func"] = func

        self.spec["subcommands"]["commands"].append(sub_spec)

        config_name = None if not issubclass(cls, ConfigUtil) else cls.config_key
        self._subcmd_config_map[sub_spec["name"]] = config_name or sub_spec["name"]

    @staticmethod
    def create_decli_spec(kls):
        """Takes a class and inspects the docstring and signature
        to generate a Decli compliant dictionary spec. Note that
        this will ignore the following variables:
        - Variables starting with an underscore
        - self, cls, args, kwargs
        
        Args:
            cls (class): Class to turn into Decli spec
        
        Returns:
            dict: Decli compliant definition
        """

        try:
            parsed_docstr = parse(kls.__doc__ or kls.__init__.__doc__)
            short_desc = parsed_docstr.short_description or ""
            long_desc = parsed_docstr.long_description or ""

            if long_desc.strip():
                desc = "\n".join(short_desc.strip(), long_desc.strip())
            else:
                desc = short_desc.strip()
            docstr_params = {
                p.arg_name: p.description.strip() for p in parsed_docstr.params
            }
        except Exception:
            logging.debug(f"Unable to parse docstring for class `{kls.__name__}`")
            desc = ""
            docstr_params = {}

        if hasattr(kls, "command_name"):
            command_name = kls.command_name
        else:
            command_name = kls.__name__
        class_sig = inspect.signature(kls)
        params = class_sig.parameters
        args = []

        for p in params.values():
            if not p.name.startswith("_") and p.name not in [
                "self",
                "cls",
                "args",
                "kwargs",
            ]:
                arg = {"name": f"--{p.name.replace('_', '-')}"}
                if p.annotation != inspect._empty:
                    arg["type"] = p.annotation
                if p.default != inspect._empty:
                    arg["default"] = p.default
                else:
                    arg["required"] = True
                if docstr_params.get(p.name):
                    arg["help"] = docstr_params.get(p.name)
                args.append(arg)

        if not re.match(r"^[A-Za-z0-9-_]+$", command_name):
            command_name = kls.__name__

        spec = {"prog": command_name, "description": desc}

        if args:
            spec["arguments"] = args

        return spec
