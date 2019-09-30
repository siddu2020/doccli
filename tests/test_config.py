import os
from unittest import TestCase

import yaml

from doccli import ConfigUtil

test_file = "testfile.yml"


class CliTool(ConfigUtil):
    command_name = "cli"

    def __init__(
        self,
        _non_cli_param: str,
        param_a: str,
        param_b: str,
        param_c: int = 5,
        *args,
        **kwargs
    ):
        """This is the command description
        
        Args:
            _non_cli_param (str): Underscore leading params aren't included in the
                                  CLI specs
            param_a: A required parameter 
            param_b: Note that the type needs to come from the annotation
            param_c: This one has a default
        """
        super().__init__(*args, **kwargs)

        self.param_a = param_a
        self.param_b = param_b
        self.param_c = param_c

        self._non_cli_param = _non_cli_param


class SuperConfig(ConfigUtil):
    config_key = "project-config"
    sub_config_list = [CliTool]
    flatten_sub_configs = False


class SuperConfigFlattened(SuperConfig):
    flatten_sub_configs = True


class TestConfigUtil(TestCase):
    def tearDown(self):
        os.remove(test_file)
        return super().tearDown()

    def test_basic_read(self):
        with open(test_file, "w+") as f:
            yaml.safe_dump({"CliTool": {"param_a": "some test value"}}, f)

        cfg: CliTool = CliTool.with_config_file(
            test_file, _non_cli_param=5, param_b="hello"
        )

        assert cfg.param_a == "some test value"
        assert cfg._non_cli_param == 5
        assert cfg.param_b == "hello"
        assert cfg.param_c == 5

    def test_basic_write(self):
        with open(test_file, "w+") as f:
            yaml.safe_dump({"CliTool": {"param_a": "some test value"}}, f)

        cfg: CliTool = CliTool.with_config_file(
            test_file, _non_cli_param=6, param_b="hello"
        )

        cfg.param_a = "a different test value"
        cfg.param_c = 6  # Not default
        cfg.to_config_file(test_file)

        with open(test_file) as f:
            contents = yaml.safe_load(f)

        self.assertDictEqual(
            contents,
            {
                "CliTool": {
                    "param_a": "a different test value",
                    "param_b": "hello",
                    "param_c": 6,
                }
            },
        )

    def test_nested_read(self):
        with open(test_file, "w+") as f:
            yaml.safe_dump(
                {"project-config": {"CliTool": {"param_a": "some test value"}}}, f
            )

        sup = SuperConfig.with_config_file(test_file, _non_cli_param=5, param_b="hello")
        cfg = sup["CliTool"]
        for cfg in [sup["CliTool"], sup["CliTool"]]:
            assert cfg.param_a == "some test value"
            assert cfg._non_cli_param == 5
            assert cfg.param_b == "hello"
            assert cfg.param_c == 5

    def test_nested_read_from_sub_config(self):
        with open(test_file, "w+") as f:
            yaml.safe_dump(
                {"project-config": {"CliTool": {"param_a": "some test value"}}}, f
            )

        cfg: CliTool = CliTool.with_config_file(
            test_file, _non_cli_param=6, param_b="hello"
        )
        assert cfg.param_a == "some test value"
        assert cfg._non_cli_param == 6
        assert cfg.param_b == "hello"
        assert cfg.param_c == 5

    def test_nested_write(self):
        with open(test_file, "w+") as f:
            yaml.safe_dump(
                {"project-config": {"CliTool": {"param_a": "some test value"}}}, f
            )

        sup = SuperConfig.with_config_file(test_file, _non_cli_param=5, param_b="hello")
        sup.to_config_file(test_file)
        with open(test_file) as f:
            contents = yaml.safe_load(f)

        self.assertDictEqual(
            contents,
            {
                "project-config": {
                    "CliTool": {"param_a": "some test value", "param_b": "hello"}
                }
            },
        )

    def test_nested_write_from_sub_config(self):
        with open(test_file, "w+") as f:
            yaml.safe_dump(
                {"project-config": {"CliTool": {"param_a": "some test value"}}}, f
            )

        cfg = CliTool.with_config_file(
            test_file, _non_cli_param=5, param_a="different value", param_b="hello"
        )
        cfg.to_config_file(test_file)
        with open(test_file) as f:
            contents = yaml.safe_load(f)

        self.assertDictEqual(
            contents,
            {
                "project-config": {
                    "CliTool": {"param_a": "different value", "param_b": "hello"}
                }
            },
        )

    def test_flattened_read(self):
        with open(test_file, "w+") as f:
            yaml.safe_dump(
                {"project-config": {}, "CliTool": {"param_a": "some test value"}}, f
            )

        sup = SuperConfigFlattened.with_config_file(
            test_file, _non_cli_param=5, param_b="hello"
        )
        cfg = sup["CliTool"]
        for cfg in [sup["CliTool"], sup["CliTool"]]:
            assert cfg.param_a == "some test value"
            assert cfg._non_cli_param == 5
            assert cfg.param_b == "hello"
            assert cfg.param_c == 5

    def test_flattened_read_from_sub_config(self):
        with open(test_file, "w+") as f:
            yaml.safe_dump(
                {"project-config": {}, "CliTool": {"param_a": "some test value"}}, f
            )

        cfg: CliTool = CliTool.with_config_file(
            test_file, _non_cli_param=6, param_b="hello"
        )
        assert cfg.param_a == "some test value"
        assert cfg._non_cli_param == 6
        assert cfg.param_b == "hello"
        assert cfg.param_c == 5

    def test_flattend_write(self):
        with open(test_file, "w+") as f:
            yaml.safe_dump(
                {"project-config": {}, "CliTool": {"param_a": "some test value"}}, f
            )

        sup = SuperConfigFlattened.with_config_file(
            test_file, _non_cli_param=5, param_b="hello"
        )
        sup.to_config_file(test_file)
        with open(test_file) as f:
            contents = yaml.safe_load(f)

        self.assertDictEqual(
            contents,
            {
                "project-config": {},
                "CliTool": {"param_a": "some test value", "param_b": "hello"},
            },
        )

    def test_flattend_write_from_sub_config(self):
        with open(test_file, "w+") as f:
            yaml.safe_dump(
                {"project-config": {}, "CliTool": {"param_a": "some test value"}}, f
            )

        cfg = CliTool.with_config_file(
            test_file, _non_cli_param=5, param_b="hello"
        )
        cfg.to_config_file(test_file)
        with open(test_file) as f:
            contents = yaml.safe_load(f)

        self.assertDictEqual(
            contents,
            {
                "project-config": {},
                "CliTool": {"param_a": "some test value", "param_b": "hello"},
            },
        )
