from typing import Dict, Any
from dataclasses import fields
from conf_root.Configuration import is_config_class
from conf_root.agents.BasicAgent import BasicAgent, MultiFileAgent
import json

from conf_root.agents.utils import data2obj


class JsonAgent(BasicAgent, MultiFileAgent):
    default_extension = '.json'

    def load(self, configuration, instance):
        super().load(configuration, instance)
        location = self.get_configuration_location(configuration)
        with open(location, encoding='utf-8') as file:
            data = json.load(file)
        # 将dict展开为对象。
        data2obj(instance, data, custom=True)
        return instance

    @staticmethod
    def obj2data(obj: Any) -> Dict[str, Any]:
        """
        递归地将dataclass实例及其嵌套的dataclass字段转换为字典。
        """
        if is_config_class(obj):
            # 对于dataclass实例，递归地处理其字段
            res = {}
            for field in fields(obj):
                value = getattr(obj, field.name)
                # 尝试获取serialize函数并调用之。
                if 'serialize' in field.metadata and (serialize_func := field.metadata['serialize']) is not None:
                    value = serialize_func(value)
                    res[field.name] = value
                    # 在进行用户自定义 serialize之后，不再进入递归。
                    continue
                res[field.name] = JsonAgent.obj2data(value)
            return res
        return obj

    def save(self, configuration, instance):
        super().save(configuration, instance)
        data = self.obj2data(instance)
        location = self.get_configuration_location(configuration)
        with open(location, "w") as file:
            json.dump(data, file)
