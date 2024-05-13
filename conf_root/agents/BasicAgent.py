import re
from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict

from conf_root.Configuration import Configuration


class BasicAgent:
    """
    类中的函数主要是处理递归问题。
    """
    default_extension: str = 'undefined'

    def __init__(self, location):
        self.path = Path(location)
        self.path.mkdir(parents=True, exist_ok=True)

    def get_configuration_location(self, configuration: Configuration) -> Path:
        invalid_chars_pattern = r'[\\/:*?"<>|]'
        filename = re.sub(invalid_chars_pattern, '_', configuration.name)
        if not filename.endswith(f'.{self.default_extension}'):
            filename += f'.{self.default_extension}'
        return self.path.joinpath(filename)

    @abstractmethod
    def exist(self, configuration: Configuration) -> bool:
        pass

    @abstractmethod
    def create(self, configuration: Configuration) -> None:
        pass

    @abstractmethod
    def load(self, configuration: Configuration) -> Dict[str, Any]:
        pass

    @abstractmethod
    def save(self, configuration: Configuration, obj: object) -> None:
        pass
