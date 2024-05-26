import os
from typing import Dict, Any, Optional

from dataclasses import fields
from conf_root.Configuration import Configuration, is_config_class
from conf_root.agents.BasicAgent import BasicAgent, MultiFileAgent
import json


class JsonAgent(BasicAgent, MultiFileAgent):
    default_extension = '.json'

    @staticmethod
    def recursive_data2obj(cls, data: Optional[Dict[str, Any]]) -> object:
        if is_config_class(cls):
            kwargs = {}
            for field in fields(cls):
                value = data.get(field.name, None)
                # 在进行用户自定义 deserialize 之后，不再进入递归流程。
                if 'deserialize' in field.metadata and (deserialize_func := field.metadata['deserialize']) is not None:
                    value = deserialize_func(value)
                    kwargs[field.name] = value
                    continue
                # 递归反序列化。
                if value is not None:
                    kwargs[field.name] = JsonAgent.recursive_data2obj(field.type, value)
            # 默认值将会在dataclass中有默认定义。
            return cls(**kwargs)
        return data

    @staticmethod
    def data2obj(instance, data: Dict[str, Any]) -> None:
        # 这个不需要加载default，因为origin_init中调用过了。
        for field in fields(instance):
            # 从字典中获取值，如果不存在则跳过
            if (value := data.get(field.name, None)) is not None:
                # 在进行用户自定义 deserialize 之后，不再进入递归流程。
                if 'deserialize' in field.metadata and (deserialize_func := field.metadata['deserialize']) is not None:
                    value = deserialize_func(value)
                else:
                    value = JsonAgent.recursive_data2obj(field.type, value)
                # 设置字段值
                setattr(instance, field.name, value)

    def load(self, configuration, instance):
        super().load(configuration, instance)
        location = self.get_configuration_location(configuration)
        with open(location, encoding='utf-8') as file:
            data = json.load(file)
        # 将dict展开为对象。
        self.data2obj(instance, data)
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
