import argparse
import dataclasses
from dataclasses import make_dataclass, field, MISSING


def argparse_to_dataclass_type(action):
    """根据argparse.Action推断dataclass字段类型"""
    if isinstance(action, argparse._StoreTrueAction) or isinstance(action, argparse._StoreFalseAction):
        return bool
    if isinstance(action, argparse._StoreConstAction):
        return type(action.const)
    if hasattr(action, 'type'):
        return action.type
    # 如果没有指定type，默认为str
    return str


def argparse_to_dataclass_default_value(action):
    """获取或推断argparse参数的默认值"""
    if (isinstance(action, argparse._StoreTrueAction) or isinstance(action, argparse._StoreFalseAction) or
            isinstance(action, argparse._StoreConstAction)):
        return field(init=False, default=action.const)
    if action.default is None:
        return field(default=MISSING)
    if isinstance(action.default, str) and action.default.lower() in ["none", "false"]:
        return field(default=MISSING)
    if action.default is argparse.SUPPRESS:
        return field(init=False, default=None)  # 对于SUPPRESS，默认值且不在初始化中
    if isinstance(action.default, bool):
        return field(default=action.default)
    else:
        return field(default=action.default)


def argparse_to_dataclass_fields(parser: argparse.ArgumentParser):
    """根据argparse.ArgumentParser生成dataclass字段定义"""
    dataclass_fields = []
    for action in parser._actions:
        if not (isinstance(action, argparse._StoreAction) or isinstance(action, argparse._StoreFalseAction) or
                isinstance(action, argparse._StoreTrueAction) or isinstance(action, argparse._StoreConstAction)):
            # 不考虑不支持的action参数
            continue
        if action.nargs not in [None, 0, 1]:  # 不考虑多参数的情况
            continue
        default_value = argparse_to_dataclass_default_value(action)
        field_type = argparse_to_dataclass_type(action)
        dataclass_fields.append((action.dest, field_type, default_value))
    return dataclass_fields


def create_dataclass_from_argparse(parser: argparse.ArgumentParser, class_name='Args'):
    """根据argparse.ArgumentParser创建对应的dataclass"""
    dataclass_fields = argparse_to_dataclass_fields(parser)
    # dataclass_fields 需排序
    dataclass_fields = sorted(dataclass_fields, key=lambda x: isinstance(x[2].default, dataclasses._MISSING_TYPE),
                              reverse=True)
    # for f in dataclass_fields:
    #     print(f)
    cls = make_dataclass(class_name, dataclass_fields)
    return cls
