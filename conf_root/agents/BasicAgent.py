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
        self.location = Path(location)
        parent_directory = self.location.parent
        parent_directory.mkdir(parents=True, exist_ok=True)

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
