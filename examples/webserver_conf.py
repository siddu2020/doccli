"""
Example showing how a config object can be used to:
- Create a CliTool
- Store config options so that they are automatically retained in a yaml file

Usage:
python webserver_conf.py --help
python webserver_conf.py run --port 8000 --hostname localhost 
python webserver_conf.py --save-cfg True run --port 8000 --hostname localhost 
python webserver_conf.py run
"""
import os
from doccli import DocCliParser, ConfigUtil


cfg_file = "webserver_conf.yml"


class Runserver(ConfigUtil):
    config_key = "server.config"
    command_name = "run"

    def __init__(self, port: int, hostname: str):
        """Initiate a server task
        
        Args:
            port (int): Port
            hostname (str): Hostname
        """
        self.port = port
        self.hostname = hostname


class WebApp(ConfigUtil):
    sub_config_list = [Runserver]

    def __init__(self, save_cfg: bool = False, *args, **kwargs):
        """Demo showing how a CLI to run a web app with config 
        could be set-up
        
        Args:
            save_cfg (bool): If true will save
             options to yaml
        """

        self.save_cfg = save_cfg
        super().__init__(*args, **kwargs)


def run_webserver(port, hostname, save_cfg):
    cfg = Runserver(port, hostname)
    print(f"Starting a server at {cfg.hostname}:{cfg.port}")
    if save_cfg:
        print(f"Saving config to {cfg_file}")
        cfg.to_config_file(cfg_file)


parser = DocCliParser(WebApp)
parser.add_subcommand(Runserver, run_webserver)

if not os.path.exists(cfg_file):
    args = parser.parse_args()
else:
    args = parser.parse_args_with_config_file(cfg_file)

params = vars(args)
func = params.pop("func")
func(**params)
