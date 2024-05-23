import logging
from dataclasses import MISSING, fields as dataclasses_fields, Field as DataclassField, is_dataclass
from typing import Any, Dict, Optional, Callable

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class ConfigurationField(DataclassField):
    def __init__(self, default, default_factory, init, repr, hash, compare, metadata,
                 serialize: Callable = MISSING, deserialize: Callable = MISSING):
        super().__init__(default, default_factory, init, repr, hash, compare, metadata)
        self.serialize = serialize
        self.deserialize = deserialize


def config_field(*, default=MISSING, default_factory=MISSING, init=True, repr=True,
                 hash=None, compare=True, metadata=None,
                 serialize: Callable = MISSING, deserialize: Callable = MISSING):
    """
    Copy from dataclass field
    """
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')
    return ConfigurationField(default, default_factory, init, repr, hash, compare,
                              metadata, serialize=serialize, deserialize=deserialize)


class Configuration:
    def __init__(self, name: str, _cls):
        self.name: str = name
        self.cls = _cls

    @staticmethod
    def field_default(field):
        if field.default is not MISSING:
            return field.default
        if field.default_factory is not MISSING:
            return field.default_factory()
        return None

    @property
    def defaults(self) -> Dict[str, Any]:
        res = {}
        for field in dataclasses_fields(self.cls):
            default = Configuration.field_default(field)
            if (serialize_func := getattr(field, 'serialize', MISSING)) != MISSING:
                res[field.name] = serialize_func(default)
                continue
            if default is not None:
                res[field.name] = Configuration.obj2data(default)
        return res

    @staticmethod
    def obj2data(obj: Any) -> Dict[str, Any]:
        """
        递归地将dataclass实例及其嵌套的dataclass字段转换为字典。
        """
        if is_dataclass(obj):
            # 对于dataclass实例，递归地处理其字段
            res = {}
            for field in dataclasses_fields(obj):
                value = getattr(obj, field.name)
                # 尝试获取serialize函数并调用之。
                if (serialize_func := getattr(field, 'serialize', MISSING)) != MISSING:
                    value = serialize_func(value)
                    res[field.name] = value
                    # 在进行用户自定义 serialize之后，不再进入递归。
                    continue
                res[field.name] = Configuration.obj2data(value)
            return res
        return obj

    @staticmethod
    def recursive_data2obj(cls, data: Optional[Dict[str, Any]]) -> object:
        if is_dataclass(cls):
            kwargs = {}
            for field in dataclasses_fields(cls):
                value = data.get(field.name, None)
                # 在进行用户自定义 deserialize 之后，不再进入递归流程。
                if (deserialize_func := getattr(field, 'deserialize', MISSING)) != MISSING:
                    value = deserialize_func(value)
                    kwargs[field.name] = value
                    continue
                # 递归反序列化。
                if value is not None:
                    kwargs[field.name] = Configuration.recursive_data2obj(field.type, value)
            # 默认值将会在dataclass中有默认定义。
            return cls(**kwargs)
        return data

    @staticmethod
    def data2obj(instance, data: Dict[str, Any]) -> None:
        # 这个不需要加载default，因为origin_init中调用过了。
        for field in dataclasses_fields(instance):
            # 从字典中获取值，如果不存在则跳过
            if (value := data.get(field.name, None)) is not None:
                # 在进行用户自定义 deserialize 之后，不再进入递归流程。
                if (deserialize_func := getattr(field, 'deserialize', MISSING)) != MISSING:
                    value = deserialize_func(value)
                else:
                    value = Configuration.recursive_data2obj(field.type, value)
                # 设置字段值
                setattr(instance, field.name, value)
