from dataclasses import MISSING, fields, is_dataclass
from typing import List, Any, Dict


def is_configuration_class(cls_or_instance):
    return getattr(cls_or_instance, '__CONF_ROOT__', None) is not None


class ConfigurationField:
    def __init__(self, _type, default=MISSING, init=True,
                 # TODO: 添加validators
                 # validators=None,
                 serialize=None, deserialize=None):
        self.type = _type
        self.default = default
        self.init = init
        # self.validators = validators
        default_serialize = lambda x: str(x)
        default_deserialize = lambda x: _type(x)
        self.serialize = serialize if serialize is not None else default_serialize
        self.deserialize = deserialize if deserialize is not None else default_deserialize


class Configuration:
    def __init__(self, name: str, fields: Dict[str, ConfigurationField]):
        self.name = name
        self.fields = fields

    @property
    def defaults(self) -> Dict[str, Any]:
        res = {}
        for label, field in self.fields.items():
            if field.default is not MISSING:
                res[label] = self.value2text(field, field.default)
        return res

    @classmethod
    def from_wrapper(cls, _class, config_name: str) -> 'Configuration':
        config_fields = {}
        for name, value in _class.__dict__.items():
            if not name.startswith('__') and not name.endswith('__'):
                # 处理用户定义的Field
                if isinstance(value, ConfigurationField):
                    config_fields[name] = value
                    setattr(_class, name, value.default)
                    continue
                # 处理类变量
                if name not in config_fields:
                    config_fields[name] = ConfigurationField(type(value), default=value)
                else:
                    config_fields[name].default = value
                    # setattr(_class, name)
        # 处理类型标记
        cls_annotation = _class.__annotations__
        for name, _type in cls_annotation.items():
            if name not in config_fields:
                config_fields[name] = ConfigurationField(_type)
            else:
                config_fields[name].type = _type
        return cls(config_name, config_fields)

    def obj2data(self, obj: object) -> Dict[str, Any]:
        """
        需避开_agent的预留值
        :param obj:
        :return:
        """
        res = {}
        for k, v in obj.__dict__.items():
            if k == '_agent':
                continue
            if k in self.fields:
                field = self.fields[k]
                res[k] = self.value2text(field, v)
            else:
                res[k] = v
        return res

    @staticmethod
    def value2text(field, value):
        if v_configuration := getattr(value, '__CONF_ROOT__', None):
            return v_configuration.obj2data(value)
        else:
            return field.serialize(value)

    def data2obj(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = {}
        for k, v in data.items():
            if k in self.fields:
                field = self.fields[k]
                if v_configuration := getattr(field.type, '__CONF_ROOT__', None):
                    sub_dict = v_configuration.data2obj(v)
                    # 这样的弊端是必须严格匹配__init__的顺序和形式；可能会出现问题。
                    value = field.type(**sub_dict)
                else:
                    # 默认将读取的数据转换为原类型。
                    value = field.deserialize(v)
                res[k] = value
            else:
                res[k] = v
        return res
