# To test run python basic.py --help

from doccli import DocCliParser

class CliTool:
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


docliparser = DocCliParser(CliTool)
parser = docliparser.parser

parser.parse_args()
