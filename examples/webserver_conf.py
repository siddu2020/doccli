"""
Example showing how a config object can be used to:
- Create a CliTool
- Store config options so that they are automatically retained in a yaml file

Usage:
python webserver_conf.py --help
python webserver_conf.py --port 8000 --hostname localhost 
python webserver_conf.py --port 8000 --hostname localhost --save-cfg True

"""
import os
from doccli import DocCliParser, ConfigUtil


cfg_file = "webserver_conf.yml"


class Webserver(ConfigUtil):
    config_key = "webserver.config"
    command = "server"

    def __init__(self, port: int, hostname: str, save_cfg: bool = False):
        """Initiate a Webserver task
        
        Args:
            port (int): Port
            hostname (str): Hostname
            save_cfg (bool): If true will save options to yaml
        """
        self.port = port
        self.hostname = hostname
        self.save_cfg = save_cfg


def run_webserver(cfg: Webserver):
    print(f"Starting a server at {cfg.hostname}:{cfg.port}")
    if cfg.save_cfg:
        print(f"Saving config to {cfg_file}")
        cfg.to_config_file(cfg_file)


parser = DocCliParser(Webserver)
args = parser.parse_args_with_config_file(cfg_file)
cfg = Webserver(**vars(args))
run_webserver(cfg)
