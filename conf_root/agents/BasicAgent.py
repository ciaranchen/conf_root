import os
import re
from abc import abstractmethod
from functools import cached_property
from pathlib import Path
from typing import Any, Dict
import logging

from conf_root.Configuration import Configuration

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class MultiFileAgent:
    default_extension: str = '.undefined'

    def __init__(self, location):
        self.path = Path(location)
        self.path.mkdir(parents=True, exist_ok=True)

    def get_configuration_location(self, configuration: Configuration) -> Path:
        filename = self.path.joinpath(configuration.filename)
        return self.ensure_suffix(filename)

    def ensure_suffix(self, path):
        # 检查文件路径是否已经有后缀名
        _, ext = os.path.splitext(path)
        # 如果后缀名不为空并且不是我们要添加的后缀名（考虑大小写）
        if ext.lower() != self.default_extension.lower():
            # 如果没有后缀名或者后缀名不同，则添加后缀名
            # 注意：这里使用os.path.basename来获取文件名，然后再拼接新的文件名和目录
            directory, filename = os.path.split(path)
            new_filename = filename + self.default_extension
            new_path = os.path.join(directory, new_filename)
            return Path(new_path)
        else:
            # 如果后缀名已经存在或者文件路径没有后缀名（即ext为空），则直接返回原路径
            return path

    def exist(self, configuration: Configuration) -> bool:
        return self.get_configuration_location(configuration).exists()


class OneFileAgent(MultiFileAgent):
    default_extension: str = '.undefined'

    def __init__(self, location):
        parent_directory = Path(location).parent
        super().__init__(parent_directory)
        self.location = self.ensure_suffix(Path(location))

    def get_configuration_location(self, configuration: Configuration) -> Path:
        return self.location

    @abstractmethod
    def exist(self, configuration: Configuration) -> bool:
        pass


class BasicAgent(MultiFileAgent):
    """
    此抽象类为所有Agent类定义接口。
    """

    @abstractmethod
    def load(self, configuration: Configuration, instance):
        logger.debug(f'load {instance.__class__.__qualname__} from: {self.get_configuration_location(configuration)}')

    @abstractmethod
    def save(self, configuration: Configuration, instance):
        logger.debug(f'save {instance.__class__.__qualname__} to: {self.get_configuration_location(configuration)}')
