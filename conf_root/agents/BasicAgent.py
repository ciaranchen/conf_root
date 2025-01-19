import os
import re
from abc import abstractmethod
import logging

logger = logging.getLogger(__name__)


class BasicAgent:
    default_extension: str = '.undefined'

    @classmethod
    def formalize_filename(cls, filename):
        invalid_chars_pattern = r'[\\/:*?"<>|]'
        filename = re.sub(invalid_chars_pattern, '_', filename)
        # 检查文件路径是否已经有后缀名
        _, ext = os.path.splitext(filename)
        # 如果后缀名不为空并且不是我们要添加的后缀名（考虑大小写）
        if ext.lower() != cls.default_extension.lower():
            # 如果没有后缀名或者后缀名不同，则添加后缀名
            # 注意：这里使用os.path.basename来获取文件名，然后再拼接新的文件名和目录
            directory, filename = os.path.split(filename)
            new_filename = filename + cls.default_extension
            new_path = os.path.join(directory, new_filename)
            return new_path
        else:
            # 如果后缀名已经存在或者文件路径没有后缀名（即ext为空），则直接返回原路径
            return filename

    def exist(self, cls) -> bool:
        return os.path.exists(cls.__CONF_LOCATION__)

    @abstractmethod
    def load(self, cls):
        logger.debug(f'load {cls.__qualname__} from: {cls.__CONF_LOCATION__}')

    @abstractmethod
    def save(self, instance):
        logger.debug(f'save {instance.__class__.__qualname__} to: {instance.__CONF_LOCATION__}')
