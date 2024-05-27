from dataclasses import fields
from typing import Optional, Dict, Any

from conf_root.Configuration import is_config_class


def recursive_data2obj(cls, data: Optional[Dict[str, Any]]) -> object:
    if is_config_class(cls):
        kwargs = {}
        for field in fields(cls):
            value = data.get(field.name, None)
            # 递归反序列化。
            if value is not None:
                kwargs[field.name] = recursive_data2obj(field.type, value)
        # 默认值将会在dataclass中有默认定义。
        return cls(**kwargs)
    return data


def data2obj(instance, data: Dict[str, Any]) -> None:
    # 这个不需要加载default，因为origin_init中调用过了。
    for field in fields(instance):
        # 从字典中获取值，如果不存在则跳过
        if (value := data.get(field.name, None)) is not None:
            value = recursive_data2obj(field.type, value)
            # 设置字段值
            setattr(instance, field.name, value)
