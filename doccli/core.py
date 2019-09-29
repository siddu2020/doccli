import argparse
import inspect
import logging
import re

from decli import cli
from docstring_parser import parse


class DocliParser:
    def __init__(self, cls):
        """Generate a Cli object from a class's docstring and signature
        
        Args:
            cls (class): Class to render as cli
        """
        spec = self.create_decli_spec(cls)
        self.spec = spec

    @property
    def parser(self) -> argparse.ArgumentParser:
        return cli(self.spec)

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

    @staticmethod
    def create_decli_spec(cls):
        """Takes a class and inspects the docstring and signature
        to generate a Decli compliant dictionary spec
        
        Args:
            cls (class): Class to turn into Decli spec
        
        Returns:
            dict: Decli compliant definition
        """

        try:
            parsed_docstr = parse(cls.__doc__ or cls.__init__.__doc__)
            command_name = parsed_docstr.short_description.strip()
            desc = parsed_docstr.long_description.strip()
            docstr_params = {
                p.arg_name: p.description.strip() for p in parsed_docstr.params
            }
        except Exception:
            logging.debug(f"Unable to parse docstring for class `{cls.__name__}`")
            command_name = ""
            desc = ""
            docstr_params = {}

        class_sig = inspect.signature(cls)
        params = class_sig.parameters
        args = []

        for p in params.values():
            if not p.name.startswith("_"):
                arg = {"name": f"--{p.name.replace('_', '-')}"}
                if p.annotation != inspect._empty:
                    arg["type"] = p.annotation
                if p.default != inspect._empty:
                    arg["default"] = p.default
                if docstr_params.get(p.name):
                    arg["help"] = docstr_params.get(p.name)
                args.append(arg)

        if not re.match(r"[A-Za-z0-9-_]+", command_name):
            command_name = cls.__name__

        spec = {"prog": command_name, "description": desc}

        if args:
            spec["arguments"] = args

        return spec
