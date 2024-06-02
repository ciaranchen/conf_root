from dataclasses import fields
from typing import Optional, Dict, Any

from conf_root.Configuration import is_config_class
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class ValidateException(BaseException):
    pass


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
                    sub_instance = cls()
                    data2obj(instance=sub_instance, data=sub_data, custom=custom)
                    value = sub_instance
                else:
                    value = value

            if 'validators' in field.metadata:
                for validator in field.metadata['validators']:
                    if not validator(value):
                        raise ValidateException(f'{field} with value {value} validate failed.')
            # 设置字段值
            setattr(instance, field.name, value)
