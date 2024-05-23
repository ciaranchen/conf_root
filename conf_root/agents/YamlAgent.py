import os.path
from ruamel.yaml import YAML

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent


class YamlAgent(BasicAgent):
    default_extension = 'yml'

    def __init__(self, location):
        super().__init__(location)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)

    def exist(self, configuration: Configuration) -> bool:
        location = self.get_configuration_location(configuration)
        return os.path.exists(location)

    def load(self, configuration):
        super().load(configuration)
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
