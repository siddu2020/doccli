"""USAGE:
python subcommands.py --help
python subcommands.py print-args --param-a h --param-b 2
"""

from doccli import DocliParser


class PrintArgs:
    def __init__(self, _non_cli_param: str, param_a: str, param_b, param_c: int = 5):
        """print-args

        Will print the provided params
        
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


docliparser = DocliParser(SuperTool)
docliparser.add_subcommand(PrintArgs, func=lambda **kwargs: print(kwargs))

args = docliparser.parser.parse_args()
args.func(**vars(args))
