import os
from pathlib import Path

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent
from conf_root.agents.YamlAgent import YamlAgent


class SingleFileYamlAgent(YamlAgent):
    """
    Similar with yaml agent, but save in single file.
    """
    default_extension: str = 'yml'

    def __init__(self, location):
        parent_directory = Path(location).parent
        super().__init__(parent_directory)
        self.location = Path(location)

    def exist(self, configuration: Configuration) -> bool:
        if not os.path.exists(self.location):
            return False
        data = self._load()
        return configuration.name in data

    def _load(self):
        if not os.path.exists(self.location):
            return {}
        with open(self.location, 'r') as f:
            return self.yaml.load(f)

    def load(self, configuration: Configuration):
        BasicAgent.load(self, configuration)
        res = self._load()
        return res[configuration.name]

    def save(self, configuration: Configuration, data) -> None:
        BasicAgent.save(self, configuration, data)
        total_data = self._load()
        total_data[configuration.name] = data

        with open(self.location, 'w') as f:
            self.yaml.dump(total_data, f)
