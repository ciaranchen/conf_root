from dataclasses import dataclass, is_dataclass
import os

from agents.YamlAgent import YamlAgent


def configuration_root(config_file: str, agent_class=YamlAgent):
    """
    类装饰器，用于从INI配置文件中加载配置或按照dataclass的默认值新建文件，
    并确保类实例化时使用这些配置。
    """

    def decorator(cls):
        if not is_dataclass(cls):
            raise TypeError(f"Target class must be a dataclass, got {cls}")

        # 自定义__post_init__
        origin_init = cls.__init__

        def decorated_init(self, *args, **kwargs):
            origin_init(self, *args, **kwargs)
            self._agent = agent_class(config_file)

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

    return decorator


@dataclass
class NestedConfig:
    n1: str = '1'


# 使用装饰器
@configuration_root('settings.yaml')
@dataclass
class AppConfig:
    not_default: str
    not_typed = 70
    nested1: NestedConfig = NestedConfig()
    database_host: str = 'localhost'
    database_port: int = 5432
    database_user: str = 'admin'
    database_password: str = 'default_password'


# 装饰器执行后，无论'settings.yaml'是否存在，在实例化时都会尝试从文件中读取值并按需使用默认值初始化
app_config = AppConfig('123')
print(app_config.__dict__)
