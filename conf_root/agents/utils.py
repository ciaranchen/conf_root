from dataclasses import fields
from typing import Optional, Dict, Any

from conf_root.Configuration import is_config_class
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class ValidateException(BaseException):
    pass


def recursive_data2obj(cls, data: Optional[Dict[str, Any]], custom=False) -> object:
    if is_config_class(cls):
        kwargs = {}
        for field in fields(cls):
            value = data.get(field.name, None)
            # 在进行用户自定义 deserialize 之后，不再进入递归流程。
            if (custom and 'deserialize' in field.metadata and
                    (deserialize_func := field.metadata['deserialize']) is not None):
                value = deserialize_func(value)
                kwargs[field.name] = value
                continue
            # 递归反序列化。
            if value is not None:
                value = recursive_data2obj(field.type, value, custom)
                if 'validators' in field.metadata:
                    for validator in field.metadata['validators']:
                        if not validator(value):
                            raise ValidateException(f'{field} with value {value} validate failed.')
                kwargs[field.name] = value
        # 默认值将会在dataclass中有默认定义。
        # TODO: 这个地方会不会有__init__的递归问题？
        return cls(**kwargs)
    return data


def data2obj(instance, data: Dict[str, Any], custom=False) -> None:
    # 这个不需要加载default，因为origin_init中调用过了。
    for field in fields(instance):
        # 从字典中获取值，如果不存在则跳过
        if (value := data.get(field.name, None)) is not None:
            # 在进行用户自定义 deserialize 之后，不再进入递归流程。
            if (custom and 'deserialize' in field.metadata and
                    (deserialize_func := field.metadata['deserialize']) is not None):
                value = deserialize_func(value)
            else:
                value = recursive_data2obj(field.type, value, custom)
            if 'validators' in field.metadata:
                for validator in field.metadata['validators']:
                    if not validator(value):
                        raise ValidateException(f'{field} with value {value} validate failed.')
            # 设置字段值
            setattr(instance, field.name, value)
