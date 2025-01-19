import os
from abc import abstractmethod
import logging

from conf_root.agents.utils import ensure_suffix, formalize_filename

logger = logging.getLogger(__name__)


class BasicAgent:
    default_extension: str = '.undefined'

    @classmethod
    def formalize_filename(cls, filename):
        filename = formalize_filename(filename)
        return ensure_suffix(filename, cls.default_extension)

    def exist(self, cls) -> bool:
        return os.path.exists(cls.__CONF_LOCATION__)

    @abstractmethod
    def load(self, cls):
        logger.debug(f'load {cls.__qualname__} from: {cls.__CONF_LOCATION__}')

    @abstractmethod
    def save(self, instance):
        logger.debug(f'save {instance.__class__.__qualname__} to: {instance.__CONF_LOCATION__}')
