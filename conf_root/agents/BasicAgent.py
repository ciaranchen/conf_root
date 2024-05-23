import re
from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict
import logging

from conf_root.Configuration import Configuration

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


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
    def load(self, configuration: Configuration) -> Dict[str, Any]:
        logger.debug(f'load from: {self.get_configuration_location(configuration)}')

    @abstractmethod
    def save(self, configuration: Configuration, data: Dict[str, Any]) -> None:
        logger.debug(f'save to: {self.get_configuration_location(configuration)}')
