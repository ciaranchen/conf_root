from dataclasses import MISSING, fields
from typing import List, Self, Any, Dict


class ConfigurationField:
    def __init__(self, label, _type, default=MISSING, validators=None, filters=None, default_factory=MISSING):
        self.label = label
        self.type = _type
        self.default = default
        self.validators = validators
        self.filters = filters
        self.default_factory = default_factory

    def serialize(self, value):
        pass

    def deserialize(self, text: str):
        pass


class Configuration:
    def __init__(self, name: str, fields: List[ConfigurationField]):
        self.name = name
        self.fields = fields

    @property
    def defaults(self) -> Dict[str, Any]:
        res = {}
        for field in self.fields:
            if field.default is not MISSING:
                res[field.label] = field.default
            elif field.default_factory is not MISSING:
                res[field.label] = field.default_factory()
        return res

    @classmethod
    def from_wrapper(cls, _class, config_name: str) -> Self:
        cls_annotation = _class.__annotations__
        config_fields = {}
        for name, _type in cls_annotation.items():
            config_fields[name] = ConfigurationField(name, _type)
        # 处理类变量
        for name, value in _class.__dict__.items():
            if not name.startswith('__') and not name.endswith('__'):
                if name not in _class.__annotations__:
                    config_fields[name] = (ConfigurationField(name, type(value), default=value))
                else:
                    config_fields[name].default = value
        return cls(config_name, list(config_fields.values()))

    def obj2data(self, obj: object) -> Dict[str, Any]:
        """
        需避开_agent的预留值
        :param obj:
        :return:
        """
        res = {k: v for k, v in obj.__dict__.items() if k != '_agent'}
        return res

    def data2obj(self, data: Dict[str, Any], obj: object):
        fields_map = {f.label: f for f in self.fields}

        for k, v in data.items():
            # 如果给出了类型，则将读取的数据转换为原类型。
            if k in fields_map:
                field = fields_map[k]
                serialize_func = getattr(field, 'serialize', field.type)
                setattr(obj, k, serialize_func(v))
            setattr(obj, k, v)
