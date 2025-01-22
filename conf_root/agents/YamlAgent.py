import logging
import os.path
from ruamel.yaml import YAML

from conf_root.agents.BasicAgent import BasicAgent

logger = logging.getLogger(__name__)


class YamlAgent(BasicAgent):
    default_extension = '.yml'

    @staticmethod
    def get_yaml():
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        return yaml

    def load(self, cls):
        super().load(cls)
        location = cls.__CONF_LOCATION__
        if not os.path.exists(location):
            return {}
        with open(location, encoding='utf-8') as file:
            # 将dict展开为对象。
            data = self.get_yaml().load(file)
        return data

    def save(self, instance):
        super().save(instance)
        location = instance.__CONF_LOCATION__
        # 将dict转换为YAML并写入文件
        data = self.model_dump(instance)
        with open(location, "w") as file:
            self.get_yaml().dump(data, file)


class SingleFileYamlAgent(YamlAgent):
    """
    Similar with yaml agent, but save in single file.
    """
    default_extension: str = '.yml'

    @staticmethod
    def class_name(cls):
        return cls.__qualname__.replace('<locals>.', '')

    def exist(self, cls) -> bool:
        return self.class_name(cls) in self._load(cls)

    def _load(self, cls):
        location = cls.__CONF_LOCATION__
        if not os.path.exists(location):
            return {}
        with open(location, 'r') as f:
            data = self.get_yaml().load(f)
        return data if data is not None else {}

    def load(self, cls):
        BasicAgent.load(self, cls)
        res = self._load(cls)
        name = self.class_name(cls)
        data = res[name]
        return data

    def save(self, instance) -> None:
        BasicAgent.save(self, instance)
        total_data = self._load(instance)
        name = self.class_name(instance.__class__)
        total_data[name] = self.model_dump(instance)

        location = instance.__CONF_LOCATION__
        with open(location, 'w') as f:
            self.get_yaml().dump(total_data, f)
