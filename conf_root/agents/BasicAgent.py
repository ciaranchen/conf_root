import os
from abc import abstractmethod
import logging

from conf_root.agents.utils import ensure_suffix, formalize_filename

logger = logging.getLogger(__name__)


class BasicAgent:
    """
    此抽象类为所有Agent类定义接口。
    """
    default_extension: str = '.undefined'

    @classmethod
    def formalize_filename(cls, filename):
        filename = formalize_filename(filename)
        return ensure_suffix(filename, cls.default_extension)

    def exist(self, instance) -> bool:
        location = instance.__CONF_LOCATION__
        return os.path.exists(location)

    @abstractmethod
    def load(self, instance):
        location = instance.__CONF_LOCATION__
        logger.debug(f'load {instance.__class__.__qualname__} from: {location}')

    @abstractmethod
    def save(self, instance):
        location = instance.__CONF_LOCATION__
        logger.debug(f'save {instance.__class__.__qualname__} to: {location}')
