from dataclasses import make_dataclass, _MISSING_TYPE, is_dataclass, fields as dataclasses_fields
from pathlib import Path
from typing import Optional, Type

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent
from conf_root.agents.YamlAgent import YamlAgent


class ConfRoot:
    def __init__(self, path: str = None, agent: Type[BasicAgent] = YamlAgent, persist: bool = True):
        self.path = Path(path) if path is not None else Path()
        self.agent_class = agent
        self.persist = persist
        self.agent_obj = self.agent_class(self.path)

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
                return _self._agent.save(configuration, _self)

            def load(_self):
                data = _self._agent.load(configuration)
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
            instance._agent = self.agent_obj
            if instance._agent.exist(configuration):
                # 如果已存在，读取和实例化
                data = instance._agent.load(configuration)
                configuration.data2obj(instance, data)
            else:
                # 若文件不存在，根据默认值创建
                instance._agent.create(configuration)

    def dataclass_from_argparse(self, parser, name='argparse'):
        configuration = Configuration.from_argparse(name, parser)
        fields = sorted([
            (name, field._type, field.default)
            for name, field in configuration.fields.items()
        ], key=lambda x: isinstance(x[2], _MISSING_TYPE), reverse=True)

        cls = make_dataclass(configuration.name, fields,
                             namespace={'__post_init__': lambda instance: self.post_init(instance, configuration)})
        setattr(cls, '__CONF_ROOT__', configuration)
        return cls

