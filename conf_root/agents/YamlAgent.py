import os.path
from typing import Any, Dict

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent
import yaml


class YamlAgent(BasicAgent):
    default_extension = 'yml'

    def exist(self, configuration: Configuration) -> bool:
        return os.path.exists(self.location)

    def create(self, configuration: Configuration):
        # 将dataclass默认值转换为dict，便于序列化
        default_dict = configuration.defaults

        # 将dict转换为YAML并写入文件
        if len(default_dict.keys()) > 0:
            with open(self.location, "w") as yaml_file:
                yaml.dump(default_dict, yaml_file)

    def load(self, configuration) -> Dict[str, Any]:
        with open(self.location, encoding='utf-8') as yaml_file:
            data = yaml.safe_load(yaml_file)
        # 将dict展开为对象。
        return configuration.data2obj(data)

    def save(self, configuration, obj):
        data_dict = configuration.obj2data(obj)
        # 将dict转换为YAML并写入文件
        with open(self.location, "w") as yaml_file:
            yaml.dump(data_dict, yaml_file)
