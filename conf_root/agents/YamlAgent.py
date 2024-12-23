import os.path
from ruamel.yaml import YAML

from conf_root.Configuration import is_config_class
from conf_root.agents.BasicAgent import BasicAgent
from conf_root.agents.utils import all_dataclass, make_serializer, class_name
from conf_root.utils import data2obj


class YamlAgent(BasicAgent):
    default_extension = '.yml'

    @staticmethod
    def get_yaml(instance):
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)

        for cls in all_dataclass(instance):
            if is_config_class(cls):
                # 'tag:yaml.org,2002:map'
                name = class_name(cls)
                representer, constructor = make_serializer(cls)
                yaml.representer.add_representer(cls, representer)
                yaml.constructor.add_constructor(f'!{name}', constructor)
            else:  # 就是普通的dataclass
                yaml.register_class(cls)
        return yaml

    def load(self, instance):
        super().load(instance)
        location = instance.__CONF_LOCATION__
        if not os.path.exists(location):
            return
        with open(location, encoding='utf-8') as file:
            # 将dict展开为对象。
            data = self.get_yaml(instance).load(file)
        # 覆盖原instance中的变量:
        data2obj(instance, data)
        return instance

    def save(self, instance):
        super().save(instance)
        location = instance.__CONF_LOCATION__
        # 将dict转换为YAML并写入文件
        with open(location, "w") as file:
            self.get_yaml(instance).dump(instance, file)


class SingleFileYamlAgent(YamlAgent):
    """
    Similar with yaml agent, but save in single file.
    """
    default_extension: str = '.yml'

    def exist(self, instance) -> bool:
        if not os.path.exists(self.location):
            return False
        data = self._load(instance)
        return class_name(instance.__class__) in data

    def _load(self, instance):
        location = instance.__CONF_LOCATION__
        if not os.path.exists(location):
            return {}
        with open(location, 'r') as f:
            data = self.get_yaml(instance).load(f)
        return data if data is not None else {}

    def load(self, instance):
        BasicAgent.load(self, instance)
        res = self._load(instance)
        name = class_name(instance.__class__)
        data = res[name]
        # 覆盖原instance中的变量
        data2obj(instance, data)
        return instance

    def save(self, instance) -> None:
        BasicAgent.save(self, instance)
        total_data = self._load(instance)
        name = class_name(instance.__class__)
        total_data[name] = instance

        with open(self.location, 'w') as f:
            self.get_yaml(instance).dump(total_data, f)
