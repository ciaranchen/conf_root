import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

from .ConfRoot import ConfRoot
from .agents.BasicAgent import BasicAgent
from .agents.JsonAgent import JsonAgent
from .agents.YamlAgent import YamlAgent, SingleFileYamlAgent
