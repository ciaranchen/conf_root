from dataclasses import make_dataclass, _MISSING_TYPE
from typing import Optional

from conf_root.Configuration import Configuration
from conf_root.agents.YamlAgent import YamlAgent


class ConfRoot:
    def __init__(self, filename: str = None, agent=YamlAgent, persist: bool = True):
        if filename is None:
            # 默认文件名: `config.yaml`
            filename = f"config.{agent.default_extension}"
        self.filename = filename
        self.agent_class = agent
        self.persist = persist
        # self.agent_obj = self.agent_class(self.filename)

    def wrap(self, *args, **kwargs):
        def decorator(cls, name: Optional[str] = None):
            name = name if name else cls.__qualname__

            configuration = Configuration.from_wrapper(cls, name)
            setattr(cls, '__CONF_ROOT__', configuration)

            # 覆盖其 __init__ 函数
            origin_init = cls.__init__

            def decorated_init(_self, *args, **kwargs):
                # do init
                for name, field in configuration.fields.items():
                    if field.init:
                        pass
                    setattr(_self, name, field.default)
                origin_init(_self, *args, **kwargs)
                self.post_init(_self, configuration)

            def save(_self):
                return _self._agent.save(configuration, _self)

            def load(_self):
                return _self._agent.load(configuration, _self)

            decorated_init.__name__ = '__init__'
            cls.__init__ = decorated_init
            if self.persist:
                cls.save = save
                cls.load = load
            return cls

        if len(args) == 1 and isinstance(args[0], type):
            # 无参数情况下，相当于直接用类的定义调用decorator.
            return decorator(args[0])
        if len(args) > 1:
            # 有args的情况下，取第一个args为 config 名称。
            return lambda cls: decorator(cls, args[0])
        else:
            # 只有kwargs的情况下，直接给回结果
            return decorator

    def post_init(self, instance, configuration):
        if self.persist:
            instance._agent = self.agent_class(self.filename)
            if instance._agent.exist(configuration):
                # 如果已存在，读取和实例化
                data = instance._agent.load(configuration)
                for k, v in data.items():
                    setattr(instance, k, v)
            else:
                # 若文件不存在，根据默认值创建
                instance._agent.create(configuration)

    def dataclass_from_argparse(self, parser):
        configuration = Configuration.from_argparse(parser)
        fields = sorted([
            (name, field._type, field.default)
            for name, field in configuration.fields.items()
        ], key=lambda x: isinstance(x[2], _MISSING_TYPE), reverse=True)

        cls = make_dataclass(configuration.name, fields,
                             namespace={'__post_init__': lambda instance: self.post_init(instance, configuration)})
        setattr(cls, '__CONF_ROOT__', configuration)
        # cls.__post_init__ = lambda instance: self.post_init(instance, configuration)
        return cls
