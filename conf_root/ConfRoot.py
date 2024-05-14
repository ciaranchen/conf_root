import argparse
from dataclasses import make_dataclass, is_dataclass, MISSING
from pathlib import Path
from typing import Optional, Type

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent
from conf_root.agents.YamlAgent import YamlAgent


class ConfRoot:
    def __init__(self, path: str = None, agent_class: Optional[Type[BasicAgent]] = YamlAgent):
        self.path = Path(path) if path is not None else Path()
        self.agent_class = agent_class
        self.persist = (agent_class is not None)
        if self.persist:
            self.agent = self.agent_class(self.path)

    def wrap(self, *args, **kwargs):
        def decorator(cls, name: Optional[str] = None):
            if not is_dataclass(cls):
                raise TypeError(f"Target class must be a dataclass, got {cls}")
            if name is None:
                name = cls.__qualname__.replace('<locals>.', '')

            configuration = Configuration.from_wrapper(cls, name)
            setattr(cls, '__CONF_ROOT__', configuration)

            # 覆盖其 __init__ 函数
            origin_init = cls.__init__

            def decorated_init(_self, *args, **kwargs):
                origin_init(_self, *args, **kwargs)
                self.post_init(_self, configuration)

            def save(_self):
                return self.agent.save(configuration, _self)

            def load(_self):
                data = self.agent.load(configuration)
                configuration.data2obj(_self, data)

            decorated_init.__name__ = '__init__'
            cls.__init__ = decorated_init
            if self.persist:
                cls.save = save
                cls.load = load
            return cls

        if len(args) == 1 and isinstance(args[0], type):
            # 无参数情况下，相当于直接用类的定义调用decorator.
            # @wrap
            return decorator(args[0], **kwargs)
        if len(args) >= 1:
            # 有args的情况下，取第一个args为 config 名称。
            # @wrap('config'）
            return lambda cls: decorator(cls, args[0])
        # 无args, 只有kwargs的情况下，直接给出decorator
        # @wrap() or @wrap(name='config')
        return lambda cls: decorator(cls, **kwargs)

    def post_init(self, instance, configuration):
        if self.persist:
            if self.agent.exist(configuration):
                # 如果已存在，读取和实例化
                data = self.agent.load(configuration)
                configuration.data2obj(instance, data)
            else:
                # 若文件不存在，根据默认值创建
                self.agent.create(configuration)

    def from_argparse(self, parser: argparse.ArgumentParser, cls_name: str = 'argparse'):
        def get_default(action):
            if isinstance(action, argparse._StoreConstAction):
                return action.const
            if action.default:
                return action.default
            if action.const:
                return action.const
            return MISSING

        def get_type(action):
            if action.type:
                return action.type
            default = get_default(action)
            if default:
                return type(default)

        fields = []
        for action in parser._actions:
            name = action.dest
            if name == 'help':
                continue
            if not (isinstance(action, argparse._StoreAction)
                    or isinstance(action, argparse._StoreFalseAction)
                    or isinstance(action, argparse._StoreTrueAction)
                    or isinstance(action, argparse._StoreConstAction)):
                # 暂不考虑不支持的action
                continue
            if action.nargs not in [None, 0, 1]:
                # 暂不考虑多参数的情况
                continue
            # TODO: handle other Action.

            if isinstance(action, argparse._StoreFalseAction):
                field = (name, bool, False)
            elif isinstance(action, argparse._StoreTrueAction):
                field = (name, bool, True)
            else:
                default = get_default(action)
                _type = get_type(action)
                field = (name, _type, default)
            fields.append(field)

        fields = sorted(fields, key=lambda x: x[2] == MISSING, reverse=True)

        cls = make_dataclass(cls_name.replace(f'.{self.agent.default_extension}', ''), fields)
        return self.wrap(cls_name)(cls)
