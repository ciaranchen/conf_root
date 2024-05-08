import os

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent
import json


class JsonAgent(BasicAgent):
    default_extension = 'json'

    def exist(self, configuration: Configuration) -> bool:
        return os.path.exists(self.location)

    def create(self, configuration: Configuration):
        # 将默认值转换为dict，便于序列化
        default_dict = configuration.defaults
        print(default_dict)

        # 将dict转换为YAML并写入文件
        if len(default_dict.keys()) > 0:
            with open(self.location, "w") as file:
                json.dump(default_dict, file)

    def load(self, configuration):
        with open(self.location, encoding='utf-8') as file:
            data = json.load(file)
        # 将dict展开为对象。
        return configuration.data2obj(data)

    def save(self, configuration, obj):
        data_dict = configuration.obj2data(obj)
        # 将dict转换为YAML并写入文件
        with open(self.location, "w") as file:
            json.dump(data_dict, file)
