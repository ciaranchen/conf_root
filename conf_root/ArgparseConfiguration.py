import argparse
import copy
import dataclasses
from dataclasses import make_dataclass, field, MISSING


class ArgparseConfiguration:
    @staticmethod
    def get_argparse_type(action):
        """根据argparse.Action推断dataclass字段类型"""
        if isinstance(action, argparse._StoreTrueAction) or isinstance(action, argparse._StoreFalseAction):
            return bool
        if isinstance(action, argparse._StoreConstAction):
            return type(action.const)
        if hasattr(action, 'type'):
            return action.type
        # 如果没有指定type，默认为str
        return str

    @staticmethod
    def get_argparse_default_value(action):
        """获取或推断argparse参数的默认值"""
        if (isinstance(action, argparse._StoreTrueAction) or isinstance(action, argparse._StoreFalseAction) or
                isinstance(action, argparse._StoreConstAction)):
            return field(default=action.const)
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

    @staticmethod
    def get_argparse_fields(parser: argparse.ArgumentParser):
        """根据argparse.ArgumentParser生成dataclass字段定义"""
        dataclass_fields = []
        unsupported_fields = []
        for action in parser._actions:
            if not (isinstance(action, argparse._StoreAction) or isinstance(action, argparse._StoreFalseAction) or
                    isinstance(action, argparse._StoreTrueAction) or isinstance(action, argparse._StoreConstAction)):
                # 不考虑不支持的action
                unsupported_fields.append(action.dest)
                continue
            if action.nargs not in [None, 0, 1]:  # 不考虑多参数的情况
                unsupported_fields.append(action.dest)
                continue
            default_value = ArgparseConfiguration.get_argparse_default_value(action)
            field_type = ArgparseConfiguration.get_argparse_type(action)
            dataclass_fields.append((action.dest, field_type, default_value))
        return dataclass_fields, unsupported_fields

    @classmethod
    def from_argparse(cls, parser: argparse.ArgumentParser, class_name='Args'):
        """根据argparse.ArgumentParser创建对应的dataclass"""
        dataclass_fields, unsupported = ArgparseConfiguration.get_argparse_fields(parser)
        # dataclass_fields 需排序
        dataclass_fields = sorted(dataclass_fields, key=lambda x: isinstance(x[2].default, dataclasses._MISSING_TYPE),
                                  reverse=True)
        # for f in dataclass_fields:
        #     print(f)
        res = cls()
        cls.dataclass = make_dataclass(class_name, dataclass_fields)
        cls.unsupported = unsupported
        return res

    def filter_unsupported(self, namespace):
        res = {}
        for key, val in vars(namespace).items():
            if key not in self.unsupported:
                res[key] = val
        return res

    def get_namespace(self, dataclass, old_namespace):
        # 仅加载配置文件的dataclass object
        object = (copy.copy(dataclass))
        object.load()
        print(object)

        res = argparse.Namespace()
        for key, val in vars(old_namespace).items():
            if key in self.unsupported:
                setattr(res, key, val)
            else:
                setattr(res, key, getattr(object, key))
        return res
