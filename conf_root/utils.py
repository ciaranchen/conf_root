from typing import Type, Any


def is_config_class(cls_or_instance: Any) -> bool:
    """检查类或实例是否是配置类"""
    return getattr(cls_or_instance, '__CONF_ROOT__', None) is not None
