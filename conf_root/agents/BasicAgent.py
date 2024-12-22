import os
from abc import abstractmethod
import logging

from conf_root.agents.utils import ensure_suffix

logger = logging.getLogger(__name__)


class BasicAgent:
    """
    此抽象类为所有Agent类定义接口。
    """

    @abstractmethod
    def initialize_location(self, filename):
        pass

    def exist(self, instance) -> bool:
        location = instance.__LOCATION__
        return os.path.exists(location)

    @abstractmethod
    def load(self, instance):
        location = instance.__LOCATION__
        logger.debug(f'load {instance.__class__.__qualname__} from: {location}')

    @abstractmethod
    def save(self, instance):
        location = instance.__LOCATION__
        logger.debug(f'save {instance.__class__.__qualname__} to: {location}')


class MultiFileAgent(BasicAgent):
    default_extension: str = '.undefined'

    def __init__(self, base_dir):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def initialize_location(self, filename):
        filename = os.path.join(self.base_dir, filename)
        return ensure_suffix(filename, self.default_extension)


class OneFileAgent(MultiFileAgent):
    default_extension: str = '.undefined'

    def __init__(self, location):
        # parent_directory = os.path.dirname(location)
        # super().__init__(parent_directory)
        self.location = ensure_suffix(location, self.default_extension)

    def initialize_location(self, name) -> str:
        return self.location
