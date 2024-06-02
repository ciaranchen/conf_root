from dataclasses import fields
from typing import Dict, Any

from conf_root.Configuration import is_config_class
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class ValidateException(BaseException):
    pass


def validate(field, value):
    if 'validators' in field.metadata:
        for validator in field.metadata['validators']:
            if not validator(value):
                raise ValidateException(f'{field} with value {value} validate failed.')


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
                cls = field.type
                if is_config_class(cls) and isinstance(value, dict):
                    sub_data = {field.name: value.get(field.name, None) for field in fields(cls)}
                    # 要求 sub_data 中的内容必须能满足初始化要求
                    sub_instance = cls(**sub_data)
                    # 后面继续做这个步骤的原因是避免从文件加载的cls内容，确保是用sub_data建立的。
                    data2obj(instance=sub_instance, data=sub_data, custom=custom)
                    value = sub_instance
                else:
                    value = value
            validate(field, value)
            # 设置字段值
            setattr(instance, field.name, value)


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
            res[field.name] = obj2data(value)
        return res
    return obj
