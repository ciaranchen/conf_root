import argparse
from dataclasses import make_dataclass, is_dataclass, MISSING, dataclass, field as dataclass_field
from pathlib import Path
from typing import Optional, Type, List
import logging

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent
from conf_root.agents.YamlAgent import YamlAgent

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class ConfRoot:
    def __init__(self, path: str = None, agent_class: Optional[Type[BasicAgent]] = YamlAgent):
        self.path = Path(path) if path is not None else Path()
        self.agent_class = agent_class
        self.persist = (agent_class is not None)
        if self.persist:
            self.agent = self.agent_class(self.path)

    def config(self, *args, **kwargs):
        def decorator(cls, name: Optional[str] = None, dynamic=False):
            if not is_dataclass(cls):
                logger.debug(f'decorate class {cls.__qualname__} to dataclass...')
                cls = dataclass(cls)
            if name is None:
                name = cls.__qualname__.replace('<locals>.', '')

            configuration = Configuration(name, cls)
            setattr(cls, '__CONF_ROOT__', configuration)

            # 覆盖其 __init__ 函数
            origin_init = cls.__init__

            def decorated_init(_self, *args, **kwargs):
                origin_init(_self, *args, **kwargs)
                self.post_init(_self, configuration)

            decorated_init.__name__ = '__init__'
            cls.__init__ = decorated_init
            if self.persist and dynamic:
                def save(_self):
                    return self.agent.save(configuration, _self)

                def load(_self):
                    return self.agent.load(configuration, _self)

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
            return lambda cls: decorator(cls, *args, **kwargs)
        # 无args, 只有kwargs的情况下，直接给出decorator
        # @wrap() or @wrap(name='config')
        return lambda cls: decorator(cls, **kwargs)

    def post_init(self, instance, configuration):
        if self.persist:
            if self.agent.exist(configuration):
                # 如果已存在，读取和实例化
                self.agent.load(configuration, instance)
            else:
                # 若文件不存在，根据默认值创建
                self.agent.save(configuration, instance)

    def from_argparse(self, parser: argparse.ArgumentParser, cls_name: str = 'ArgparseConfig'):
        def get_default(action):
            if action.default and action.default != argparse.SUPPRESS:
                return action.default
            if action.const and isinstance(action, argparse._StoreConstAction):
                return action.const
            # 如果是Required的话，那么传入的参数中必定有它，所以不必有default。
            return MISSING if action.required else None  # 实在没有default的话，就先给None了

        def get_type(action):
            if action.type:
                return action.type
            if action.nargs and action.nargs != '?':
                return List
            if (isinstance(action, argparse._AppendAction) or
                    isinstance(action, argparse._AppendConstAction) or isinstance(action, argparse._ExtendAction)):
                return List
            default = get_default(action)
            if default:
                return type(default)

        def default_field(action):
            metadata = {'validators': []}
            if action.help:
                metadata['comment'] = action.help
            # validators
            if action.choices:
                metadata['validators'].append(lambda x: x in action.choices)
            if action.nargs:
                if isinstance(action.nargs, int):
                    metadata['validators'].append(lambda x: len(x) == action.nargs)
                if action.nargs == '+':
                    metadata['validators'].append(lambda x: len(x) > 0)
            return dataclass_field(default=get_default(action), metadata=metadata)

        fields = []
        for action in parser._actions:
            name = action.dest
            if isinstance(action, argparse._HelpAction) or isinstance(action, argparse._VersionAction):
                continue
            _SUPPORT_ACTIONS = [
                argparse._AppendAction, argparse._AppendConstAction, argparse._CountAction, argparse._ExtendAction,
                argparse._StoreAction, argparse._StoreConstAction, argparse._StoreFalseAction, argparse._StoreTrueAction
            ]
            if not any([isinstance(action, sa) for sa in _SUPPORT_ACTIONS]):
                logger.warning(f'Skiped Argparse: {action.dest} action {action.__class__.__name__}')
                # 暂不考虑不支持的action
                continue
            # TODO: handle other Action.

            _type = get_type(action)
            field = (name, _type, default_field(action))
            fields.append(field)
            print(field)

        fields = sorted(fields, key=lambda x: x[2].default == MISSING, reverse=True)

        cls = make_dataclass(cls_name.replace(f'.{self.agent.default_extension}', ''), fields)
        return self.config(cls)
