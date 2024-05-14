import os.path
from typing import Any, Dict

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent
from ruamel.yaml import YAML


class YamlAgent(BasicAgent):
    default_extension = 'yml'

    def __init__(self, location):
        super().__init__(location)
        self.yaml = YAML(typ='safe')

    def exist(self, configuration: Configuration) -> bool:
        location = self.get_configuration_location(configuration)
        return os.path.exists(location)

    def create(self, configuration: Configuration):
        super().create(configuration)
        location = self.get_configuration_location(configuration)
        # 将dataclass默认值转换为dict，便于序列化
        default_dict = configuration.defaults

        # 将dict转换为YAML并写入文件
        if len(default_dict.keys()) > 0:
            with open(location, "w") as file:
                self.yaml.dump(default_dict, file)

    def load(self, configuration) -> Dict[str, Any]:
        super().load(configuration)
        location = self.get_configuration_location(configuration)
        with open(location, encoding='utf-8') as file:
            data = self.yaml.load(file)
        # 将dict展开为对象。
        return data

    def save(self, configuration, obj):
        super().save(configuration, obj)
        location = self.get_configuration_location(configuration)
        data_dict = configuration.obj2data(obj)
        # 将dict转换为YAML并写入文件
        with open(location, "w") as file:
            self.yaml.dump(data_dict, file)
