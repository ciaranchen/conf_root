import logging
import re
from dataclasses import MISSING, fields as dataclasses_fields, dataclass
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def is_config_class(cls_or_instance):
    return getattr(cls_or_instance, '__CONF_ROOT__', None) is not None


@dataclass
class Configuration:
    name: str
    cls: Any

    @property
    def filename(self):
        invalid_chars_pattern = r'[\\/:*?"<>|]'
        filename = re.sub(invalid_chars_pattern, '_', self.name)
        return filename

    @property
    def fields(self):
        return dataclasses_fields(self.cls)

    @staticmethod
    def field_default(field):
        if field.default is not MISSING:
            return field.default
        if field.default_factory is not MISSING:
            return field.default_factory()
        return None

    @staticmethod
    def defaults(instance) -> Dict[str, Any]:
        res = {}
        for field in dataclasses_fields(instance):
            default = Configuration.field_default(field)
            if 'serialize' in field.metadata and (serialize_func := field.metadata['serialize']) is not None:
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
        if is_config_class(obj):
            # 对于dataclass实例，递归地处理其字段
            res = {}
            for field in dataclasses_fields(obj):
                value = getattr(obj, field.name)
                # 尝试获取serialize函数并调用之。
                if 'serialize' in field.metadata and (serialize_func := field.metadata['serialize']) is not None:
                    value = serialize_func(value)
                    res[field.name] = value
                    # 在进行用户自定义 serialize之后，不再进入递归。
                    continue
                res[field.name] = Configuration.obj2data(value)
            return res
        return obj

    @staticmethod
    def recursive_data2obj(cls, data: Optional[Dict[str, Any]]) -> object:
        if is_config_class(cls):
            kwargs = {}
            for field in dataclasses_fields(cls):
                value = data.get(field.name, None)
                # 在进行用户自定义 deserialize 之后，不再进入递归流程。
                if 'deserialize' in field.metadata and (deserialize_func := field.metadata['deserialize']) is not None:
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
                if 'deserialize' in field.metadata and (deserialize_func := field.metadata['deserialize']) is not None:
                    value = deserialize_func(value)
                else:
                    value = Configuration.recursive_data2obj(field.type, value)
                # 设置字段值
                setattr(instance, field.name, value)
