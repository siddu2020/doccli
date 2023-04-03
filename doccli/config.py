import inspect
import collections
from typing import List, Dict, Type, TypeVar

import yaml


T = TypeVar("T", bound="ConfigUtil")


class ConfigUtil:
    config_key: str = None
    flatten_sub_configs: bool = True
    sub_config_list: List[T] = []

    def __init__(self, _config_dict={}, **kwargs):
        self._ss = {}
        for ss in self.sub_config_list:
            self.subconfigs[ss.get_config_key()] = ss.with_config_dict(
                _config_dict, **kwargs
            )

    @property
    def subconfigs(self):
        if hasattr(self, "_ss"):
            return self._ss
        else:
            return {}

    @staticmethod
    def _get_config_key_repr(s: str):
        return f"{s}"

    def __getitem__(self, item):
        try:
            return self.subconfigs[item]
        except KeyError:
            return self.subconfigs[self._get_config_key_repr(item)]

    def get(self, item, missing=None):
        try:
            return self[item]
        except KeyError:
            return missing

    @classmethod
    def get_config_key(cls):
        return cls._get_config_key_repr(cls.config_key or cls.__name__)

    @staticmethod
    def _get_sub_dict_by_key(k: str, d: Dict) -> Dict:
        """Rursively search a dict until we find a dict that has key k
        
        Args:
            k (str): key
            d (Dict): dict
        
        Returns:
            Dict: Sub dictionary
        """
        if not isinstance(d, collections.abc.Mapping):
            return {}
        if k in d:
            return d
        else:
            for val in d.values():
                sub_dict = ConfigUtil._get_sub_dict_by_key(k, val)
                if sub_dict:
                    return sub_dict
        return {}

    def _convert_config_params(self) -> Dict:
        class_sig = inspect.signature(self.__class__)
        params = class_sig.parameters

        config_items = {}
        for p in params.values():
            if not p.name.startswith("_") and hasattr(self, p.name):
                if getattr(self, p.name) != p.default:
                    config_items[p.name] = getattr(self, p.name)
        return config_items

    def to_config_dict(self, flatten: bool = None) -> Dict:
        """Converts a config object into dictionary. Values are only pulled
        from the __init__ method, and the instantiated parameters must have the
        same names as the __init__ parameters.

        - Parameters that start with an underscore are ignored
        - Sub_config_lists are rendered recursively 
        - If ConfigUtil.flatten_sub_configs is true, then sub_config_lists are written at the same
          level

        Returns:
            Dict: Object rendered as dict
        """
        key = self.get_config_key()
        config_items = {key: self._convert_config_params()}
        for ss_key, ss in self.subconfigs.items():
            ss_dict = ss.to_config_dict()

            if self.flatten_sub_configs:
                config_items.update(**ss_dict)
            else:
                config_items[key].update(**ss_dict)

        return config_items

    def to_config_file(self, filename: str):
        """Converts a config object into a dictionary using to_config_dict, and then 
        writes the contents to the relevant section, reading in the file first
        
        Args:
            filename (str): Path to yml config file
        """
        try:
            with open(filename, "r+") as f:
                contents = yaml.safe_load(f)
        except FileNotFoundError:
            contents = {}

        config_dict = self.to_config_dict()
        sub_contents = self._get_sub_dict_by_key(self.get_config_key(), contents)
        if not sub_contents:
            contents.update(**config_dict)
        else:
            sub_contents.update(**config_dict)
        with open(filename, "w+") as f:
            contents = yaml.safe_dump(contents, f, default_flow_style=False)

    @classmethod
    def with_config_dict(cls: Type[T], config_dict: Dict, **kwargs) -> Type[T]:
        """Instantiate class from a ConfigUtil dictionary, with additional 
        kwargs to fill in unprovided values
        
        Args:
            config_dict (Dict): Values matching config dict
        
        Returns:
            cls: The instantiated class
        """
        cls_config_dict = config_dict.pop(cls.get_config_key(), dict())
        cls_config_dict.update(**kwargs)

        # Clean up cls_config_dict to match expected params
        param_names = [p for p in inspect.signature(cls).parameters.keys()]
        if "kwargs" not in param_names:
            cls_config_dict = {
                k: v for k, v in cls_config_dict.items() if k in param_names
            }

        if len(cls.sub_config_list) == 0:
            return cls(**cls_config_dict)

        if cls.flatten_sub_configs:
            cls_config_dict.update(**config_dict)

        return cls(_config_dict=cls_config_dict, **cls_config_dict)

    @classmethod
    def with_config_file(cls: Type[T], filename: str, **kwargs) -> Type[T]:
        """Instantiate this class, uing a YML file to 
        prepopulate values that aren't provided in kwargs.

        This still works if the file doesn't contain the config 
        at the top level - however it does keyscrape and could 
        break if the [[ config_key ]] is found as a key in a configurable
        parameter within the dictionary.
        
        Args:
            filename (str): Path to config file
        """
        try:
            with open(filename, "r+") as f:
                contents = yaml.safe_load(f)
        except FileNotFoundError:
            contents = {}

        contents = cls._get_sub_dict_by_key(cls.get_config_key(), contents)

        return cls.with_config_dict(contents, **kwargs)
