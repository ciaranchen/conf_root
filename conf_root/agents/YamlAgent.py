import os.path
from ruamel.yaml import YAML

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent, OneFileAgent


class YamlAgent(BasicAgent):
    default_extension = '.yml'

    def __init__(self, location):
        super().__init__(location)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)

    def exist(self, configuration: Configuration) -> bool:
        location = self.get_configuration_location(configuration)
        return os.path.exists(location)

    def load(self, configuration, instance):
        super().load(configuration, instance)
        location = self.get_configuration_location(configuration)
        if not os.path.exists(location):
            return {}
        with open(location, encoding='utf-8') as file:
            # 将dict展开为对象。
            return self.yaml.load(file)

    def save(self, configuration, data):
        super().save(configuration, data)
        location = self.get_configuration_location(configuration)
        if not os.path.exists(location) and len(data.keys()) == 0:
            return
        # 将dict转换为YAML并写入文件
        with open(location, "w") as file:
            self.yaml.dump(data, file)


class SingleFileYamlAgent(YamlAgent, OneFileAgent):
    """
    Similar with yaml agent, but save in single file.
    """
    default_extension: str = '.yml'

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

    def load(self, configuration: Configuration, instance):
        BasicAgent.load(self, configuration, instance)
        res = self._load()
        return res[configuration.name]

    def save(self, configuration: Configuration, data) -> None:
        BasicAgent.save(self, configuration, data)
        total_data = self._load()
        total_data[configuration.name] = data

        with open(self.location, 'w') as f:
            self.yaml.dump(total_data, f)
