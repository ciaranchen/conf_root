import os
from ruamel.yaml import YAML

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent


class RuamelYamlAgent(BasicAgent):
    """
    Similar with yaml agent, but save in single file.
    """
    default_extension: str = 'yaml'

    def __init__(self, location):
        super().__init__(location)
        self.yaml_parser = YAML()
        self.yaml_parser.preserve_quotes = True
        self.yaml_parser.indent(mapping=2, sequence=4, offset=2)
        self.data = {}

    def exist(self, configuration: Configuration) -> bool:
        if not os.path.exists(self.location):
            return False
        self.data = self._load()
        return configuration.name in self.data

    def create(self, configuration: Configuration) -> None:
        self.data[configuration.name] = configuration.defaults

        with open(self.location, 'w') as f:
            self.yaml_parser.dump(self.data, f)

    def _load(self):
        with open(self.location, 'r') as f:
            return self.yaml_parser.load(f)

    def load(self, configuration: Configuration) -> None:
        data = self._load()
        configuration.data2obj(data[configuration.name])

    def save(self, configuration: Configuration, obj: object) -> None:
        total_data = self._load()

        data = configuration.obj2data(obj)
        total_data[configuration.name] = data

        with open(self.location, 'w') as f:
            self.yaml_parser.dump(total_data, f)
