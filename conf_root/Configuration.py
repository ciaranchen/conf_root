import argparse
import logging
from dataclasses import MISSING, fields as dataclasses_fields, Field as DataclassField, is_dataclass
from typing import List, Any, Dict, Type, Optional

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class Configuration:
    def __init__(self, name: str, fields: Dict[str, DataclassField]):
        self.name: str = name
        self.fields: Dict[str, DataclassField] = fields

    @property
    def defaults(self) -> Dict[str, Any]:
        res = {}
        for name, field in self.fields.items():
            if field.default is not MISSING:
                res[name] = self.obj2data(field.default)
                continue
            if field.default_factory is not MISSING:
                res[name] = self.obj2data(field.default_factory())
                continue
        return res

    def obj2data(self, obj: Any) -> Dict[str, Any]:
        """
        递归地将dataclass实例及其嵌套的dataclass字段转换为字典。
        """
        if is_dataclass(obj):
            # 对于dataclass实例，递归地处理其字段
            return {f.name: self.obj2data(getattr(obj, f.name)) for f in dataclasses_fields(obj)}
        return obj

    @staticmethod
    def recursive_data2obj(cls: Type, data: Dict[str, Any]) -> object:
        # 这个需要加载default
        kwargs = {}
        for field in dataclasses_fields(cls):
            if is_dataclass(field.type):
                item = data.get(field.name, None)
                if item is None:
                    kwargs[field.name] = field.default
                else:
                    kwargs[field.name] = Configuration.recursive_data2obj(field.type, item)
            else:
                kwargs[field.name] = data.get(field.name, field.default)
        return cls(**kwargs)

    @staticmethod
    def data2obj(instance, data: Dict[str, Any]) -> None:
        # 这个不需要加载default，因为origin_init中调用过了。
        for field in dataclasses_fields(instance):
            # 从字典中获取值，如果不存在则跳过
            if (value := data.get(field.name, None)) is not None:
                if is_dataclass(field.type):
                    value = Configuration.recursive_data2obj(field.type, value)
                # 设置字段值
                setattr(instance, field.name, value)

    @classmethod
    def from_wrapper(cls, _class, config_name: str) -> 'Configuration':
        fields = {}
        for field in dataclasses_fields(_class):
            fields[field.name] = field
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
