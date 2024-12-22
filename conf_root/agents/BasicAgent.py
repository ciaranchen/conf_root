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

    def exist(self, location) -> bool:
        return os.path.exists(location)

    @abstractmethod
    def load(self, location, instance):
        logger.debug(f'load {instance.__class__.__qualname__} from: {location}')

    @abstractmethod
    def save(self, location, instance):
        logger.debug(f'save {instance.__class__.__qualname__} to: {location}')


class MultiFileAgent(BasicAgent):
    default_extension: str = '.undefined'

    def __init__(self, location):
        self.path = location
        os.makedirs(self.path, exist_ok=True)

    def initialize_location(self, filename):
        filename = os.path.join(self.path, filename)
        return ensure_suffix(filename, self.default_extension)


class OneFileAgent(MultiFileAgent):
    default_extension: str = '.undefined'

    def __init__(self, location):
        parent_directory = os.path.dirname(location)
        super().__init__(parent_directory)
        self.location = ensure_suffix(location, self.default_extension)

    def initialize_location(self, name) -> str:
        return self.location
