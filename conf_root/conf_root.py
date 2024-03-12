from dataclasses import dataclass, is_dataclass
import os

from .agents.YamlAgent import YamlAgent


def configuration(*args, agent=YamlAgent):
    """
    类装饰器。
    1. 检测是否存在配置文件(默认文件名: `config.yaml`) ，如果不存在则按照默认值新建文件。
    2. 如存在配置文件，则加载文件中的配置。
    3. 提供存储和加载的接口，可供动态改动。
    """

    def decorator(cls, config_file: str = f"config.{agent.default_extension}"):
        if not is_dataclass(cls):
            raise TypeError(f"Target class must be a dataclass, got {cls}")

        # 自定义__post_init__
        origin_init = cls.__init__

        def decorated_init(self, *args, **kwargs):
            origin_init(self, *args, **kwargs)
            self._agent = agent(config_file)

            if os.path.exists(config_file):
                # 如果文件已存在，正常处理读取和实例化逻辑
                self._agent.load(cls, self)
            else:
                # 若文件不存在，根据dataclass的默认值创建
                self._agent.create(cls)

        def save(self):
            self._agent.save(self)

        def load(self):
            self._agent.load(cls, self)

        decorated_init.__name__ = '__init__'
        cls.__init__ = decorated_init
        cls.save = save
        cls.load = load
        return cls

    if len(args) == 1 and isinstance(args[0], type):
        # 无参数情况下，相当于直接用类的定义调用decorator.
        return decorator(args[0])
    if len(args) > 0:
        # 有args的情况下，取第一个args为 config 文件名。
        return lambda cls: decorator(cls, config_file=args[0])
    # 只有kwargs的情况下，直接给回结果
    return decorator
