import argparse
import logging
from dataclasses import MISSING, dataclass
from typing import List, Any, Dict

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def is_configuration_class(cls_or_instance):
    return getattr(cls_or_instance, '__CONF_ROOT__', None) is not None


@dataclass
class ConfigurationField:
    _type: type
    default: Any = MISSING
    # init: bool = True
    # TODO: 添加validators
    # validators=None


class Configuration:
    def __init__(self, name: str, fields: Dict[str, ConfigurationField]):
        self.name = name
        self.fields = fields

    @staticmethod
    def value2text(value):
        if v_configuration := getattr(value, '__CONF_ROOT__', None):
            return v_configuration.obj2data(value)
        else:
            return value

    @property
    def defaults(self) -> Dict[str, Any]:
        res = {}
        for label, field in self.fields.items():
            if field.default is not MISSING:
                res[label] = self.value2text(field.default)
        return res

    def obj2data(self, obj: object) -> Dict[str, Any]:
        res = {}
        for k, v in obj.__dict__.items():
            # 需避开_agent的预留值
            if k == '_agent':
                continue
            if k in self.fields:
                field = self.fields[k]
                res[k] = self.value2text(v)
            else:
                res[k] = v
        return res

    def data2obj(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = {}
        for k, v in data.items():
            if k in self.fields:
                field = self.fields[k]
                if v_configuration := getattr(field._type, '__CONF_ROOT__', None):
                    sub_dict = v_configuration.data2obj(v)
                    # 这样的弊端是必须严格匹配__init__的顺序和形式；可能会出现问题。
                    value = field._type(**sub_dict)
                else:
                    # 默认将读取的数据转换为原类型。
                    value = field._type(v)
                res[k] = value
            else:
                res[k] = v
        return res

    @classmethod
    def from_wrapper(cls, _class, config_name: str) -> 'Configuration':
        fields = {}
        for name, value in _class.__dict__.items():
            if not name.startswith('__') and not name.endswith('__'):
                # 处理用户定义的Field
                if isinstance(value, ConfigurationField):
                    fields[name] = value
                    setattr(_class, name, value.default)
                    continue
                # 处理类变量
                if name not in fields:
                    fields[name] = ConfigurationField(type(value), default=value)
                else:
                    fields[name].default = value
                    # setattr(_class, name)
        # 处理类型标记
        cls_annotation = _class.__annotations__
        for name, _type in cls_annotation.items():
            if name not in fields:
                fields[name] = ConfigurationField(_type, default=MISSING)
            else:
                fields[name]._type = _type
        logger.debug(config_name)
        logger.debug(fields)
        return cls(config_name, fields)

    @classmethod
    def from_argparse(cls, conf_name: str, parser: argparse.ArgumentParser):
        def get_default(action):
            if isinstance(action, argparse._StoreConstAction):
                return action.const
            if action.default:
                return action.default
            if action.const:
                return action.const
            return MISSING

        def get_type(action):
            if action.type:
                return action.type
            default = get_default(action)
            if default:
                return type(default)

        fields = {}
        for action in parser._actions:
            name = action.dest
            if name == 'help':
                continue
            if not (isinstance(action, argparse._StoreAction)
                    or isinstance(action, argparse._StoreFalseAction)
                    or isinstance(action, argparse._StoreTrueAction)
                    or isinstance(action, argparse._StoreConstAction)):
                # 暂不考虑不支持的action
                continue
            if action.nargs not in [None, 0, 1]:
                # 暂不考虑多参数的情况
                continue
            # TODO: handle other Action.

            if isinstance(action, argparse._StoreFalseAction):
                field = ConfigurationField(bool, default=False)
            elif isinstance(action, argparse._StoreTrueAction):
                field = ConfigurationField(bool, default=True)
            else:
                default = get_default(action)
                _type = get_type(action)
                field = ConfigurationField(_type, default=default)
            fields[name] = field
        return cls(conf_name, fields)
