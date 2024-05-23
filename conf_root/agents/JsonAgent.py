import os

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent
import json


class JsonAgent(BasicAgent):
    default_extension = 'json'

    def exist(self, configuration: Configuration) -> bool:
        return self.get_configuration_location(configuration).exists()

    def load(self, configuration):
        super().load(configuration)
        location = self.get_configuration_location(configuration)
        with open(location, encoding='utf-8') as file:
            data = json.load(file)
        # 将dict展开为对象。
        return data

    def save(self, configuration, data):
        super().save(configuration, data)
        location = self.get_configuration_location(configuration)
        if not os.path.exists(location) and len(data.keys()) == 0:
            return

        # 将dict转换为YAML并写入文件
        with open(location, "w") as file:
            json.dump(data, file)
