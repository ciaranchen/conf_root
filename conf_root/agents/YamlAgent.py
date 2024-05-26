import dataclasses
import os.path
from ruamel.yaml import YAML, SafeRepresenter

from conf_root.Configuration import Configuration
from conf_root.agents.BasicAgent import BasicAgent, OneFileAgent


class MyDataRepresenter(SafeRepresenter):
    def represent_dataclass(self, data):
        # 自定义序列化逻辑
        mapping = {}
        for field in dataclasses.fields(data):
            if 'serialize' in field.metadata:
                # 特殊处理具有自定义元数据的字段
                serialize_func = field.metadata['serialize']
                field_value = getattr(data, field.name)
                value = self.represent_scalar('tag: yaml.org,2002:str', serialize_func(field_value))
                # value = self.represent_custom(getattr(data, field.name), field.metadata['serialize_as'])
            else:
                # 默认序列化其他字段
                value = self.represent_data(getattr(data, field.name))
            mapping[field.name] = value
        # 返回映射的表示
        return self.represent_mapping(None, mapping)


class YamlAgent(BasicAgent):
    default_extension = '.yml'

    @staticmethod
    def get_yaml(configuration: Configuration):
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)

        classes = configuration.yaml_register_classes()
        for cls in classes:
            yaml.register_class(cls)
        return yaml

    def load(self, configuration, instance):
        super().load(configuration, instance)
        location = self.get_configuration_location(configuration)
        if not os.path.exists(location):
            return
        with open(location, encoding='utf-8') as file:
            # 将dict展开为对象。
            data = self.get_yaml(configuration).load(file)
        # 覆盖原instance中的变量:
        for k, v in data.__dict__.items():
            setattr(instance, k, v)
        return instance

    def save(self, configuration, instance):
        super().save(configuration, instance)
        location = self.get_configuration_location(configuration)
        # 将dict转换为YAML并写入文件
        with open(location, "w") as file:
            self.get_yaml(configuration).dump(instance, file)


class SingleFileYamlAgent(YamlAgent, OneFileAgent):
    """
    Similar with yaml agent, but save in single file.
    """
    default_extension: str = '.yml'

    def exist(self, configuration: Configuration) -> bool:
        if not os.path.exists(self.location):
            return False
        data = self._load(configuration)
        return configuration.name in data

    def _load(self, configuration):
        if not os.path.exists(self.location):
            return {}
        with open(self.location, 'r') as f:
            return self.get_yaml(configuration).load(f)

    def load(self, configuration: Configuration, instance):
        BasicAgent.load(self, configuration, instance)
        res = self._load(configuration)
        data = res[configuration.name]
        # 覆盖原instance中的变量:
        for k, v in data.__dict__.items():
            setattr(instance, k, v)
        return instance

    def save(self, configuration: Configuration, instance) -> None:
        BasicAgent.save(self, configuration, instance)
        total_data = self._load(configuration)
        total_data[configuration.name] = instance

        with open(self.location, 'w') as f:
            self.get_yaml(configuration).dump(total_data, f)
