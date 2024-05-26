import argparse
from dataclasses import make_dataclass, is_dataclass, MISSING, dataclass
from pathlib import Path
from typing import Optional, Type
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
                    data = configuration.obj2data(_self)
                    return self.agent.save(configuration, data)

                def load(_self):
                    data = self.agent.load(configuration, _self)
                    configuration.data2obj(_self, data)

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
                data = self.agent.load(configuration, instance)
                configuration.data2obj(instance, data)
            else:
                # 若文件不存在，根据默认值创建
                data = configuration.defaults(instance)
                self.agent.save(configuration, data)

    def from_argparse(self, parser: argparse.ArgumentParser, cls_name: str = 'ArgparseConfig'):
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
        return self.config(cls)
