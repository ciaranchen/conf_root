from dataclasses import make_dataclass, field
import argparse
from typing import Any, List, Optional


def argparse_to_dataclass_type(action):
    """根据argparse.Action推断dataclass字段类型"""
    if hasattr(action, 'type'):
        if action.nargs in [None, 1]:  # 默认处理
            return action.type
        elif action.nargs in ['?', '*']:  # 可选或任意数量参数
            return Optional[action.type]
        elif action.nargs == '+':  # 一个或多个参数
            return List[action.type]
    return str  # 如果没有指定type，默认为str


def get_default_value(action):
    """获取或推断argparse参数的默认值"""
    if isinstance(action.default, str) and action.default.lower() in ["none", "false"]:
        return None
    elif action.default is argparse.SUPPRESS:
        return field(init=False, default=None)  # 对于SUPPRESS或const，默认值且不在初始化中
    elif isinstance(action.default, bool):
        return field(default=action.default)
    else:
        return field(default=action.default)


def argparse_to_dataclass_fields(parser: argparse.ArgumentParser):
    """根据argparse.ArgumentParser生成dataclass字段定义"""
    dataclass_fields = []
    for action in parser._actions:
        if action.dest == 'help':
            continue
        default_value = get_default_value(action)
        field_type = argparse_to_dataclass_type(action)
        dataclass_fields.append((action.dest, field_type, default_value))
    return dataclass_fields


def create_dataclass_from_argparse(parser: argparse.ArgumentParser, class_name='Args'):
    """根据argparse.ArgumentParser创建对应的dataclass"""
    dataclass_fields = argparse_to_dataclass_fields(parser)
    cls = make_dataclass(class_name, dataclass_fields)
    return cls
