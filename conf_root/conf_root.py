from dataclasses import is_dataclass
from typing import Optional

from conf_root.Configuration import Configuration
from conf_root.agents.YamlAgent import YamlAgent


class ConfRoot:
    def __init__(self, filename: str = None, agent=YamlAgent):
        if filename is None:
            # 默认文件名: `config.yaml`
            filename = f"config.{agent.default_extension}"
        self.filename = filename
        self.agent_class = agent
        # self.agent_obj = self.agent_class(self.filename)

    def wrap(self, *args, try_load=True):
        def decorator(cls, name: Optional[str] = None, try_load: bool = True):
            name = name if name else cls.__qualname__

            configuration = Configuration.from_wrapper(cls, name)
            setattr(cls, '__CONF_ROOT__', configuration)

            # 覆盖其 __init__ 函数
            origin_init = cls.__init__

            def decorated_init(_self, *args, **kwargs):
                origin_init(_self, *args, **kwargs)
                _self._agent = self.agent_class(self.filename)

                if _self._agent.exist(configuration):
                    # 如果已存在，读取和实例化
                    _self._agent.load(configuration, _self)
                else:
                    # 若文件不存在，根据默认值创建
                    _self._agent.create(configuration)

            def save(_self):
                return _self._agent.save(configuration, _self)

            def load(self):
                return self._agent.load(configuration, self)

            decorated_init.__name__ = '__init__'
            cls.__init__ = decorated_init
            cls.save = save
            cls.load = load
            return cls

        if len(args) == 1 and isinstance(args[0], type):
            # 无参数情况下，相当于直接用类的定义调用decorator.
            return decorator(args[0])
        if len(args) > 1:
            # 有args的情况下，取第一个args为 config 名称。
            return lambda cls: decorator(cls, args[0], try_load=try_load)
        else:
            # 只有kwargs的情况下，直接给回结果
            return decorator
