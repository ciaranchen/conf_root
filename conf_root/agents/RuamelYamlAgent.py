import os
from pathlib import Path

from ruamel.yaml import YAML

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent


class RuamelYamlAgent(BasicAgent):
    """
    Similar with yaml agent, but save in single file.
    """
    default_extension: str = 'yml'

    def __init__(self, location):
        parent_directory = Path(location).parent
        super().__init__(parent_directory)
        self.location = Path(location)

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
        super().create(configuration)
        self.data[configuration.name] = configuration.defaults

        with open(self.location, 'w') as f:
            self.yaml_parser.dump(self.data, f)

    def _load(self):
        with open(self.location, 'r') as f:
            return self.yaml_parser.load(f)

    def load(self, configuration: Configuration) -> None:
        super().load(configuration)
        data = self._load()
        configuration.data2obj(data[configuration.name])

    def save(self, configuration: Configuration, obj: object) -> None:
        super().save(configuration, obj)
        total_data = self._load()

        data = configuration.obj2data(obj)
        total_data[configuration.name] = data

        with open(self.location, 'w') as f:
            self.yaml_parser.dump(total_data, f)
