import dataclasses
import os.path
from ruamel.yaml import YAML, CommentedMap

from conf_root.Configuration import Configuration, is_config_class
from conf_root.agents.BasicAgent import BasicAgent, OneFileAgent
from conf_root.utils import data2obj


def make_serializer(cls):
    name = cls.__CONF_ROOT__.name

    def config_class_representer(dumper, data):
        data_dict = CommentedMap()
        for field in dataclasses.fields(data):
            value = getattr(data, field.name)
            if 'serialize' in field.metadata:
                serialize_func = field.metadata['serialize']
                data_dict[field.name] = serialize_func(value)
            else:
                data_dict[field.name] = value
            if 'comment' in field.metadata:
                data_dict.yaml_add_eol_comment(field.metadata['comment'], key=field.name)
        return dumper.represent_mapping(f'!{name}', data_dict)

    def config_class_constructor(loader, node):
        data_dict = loader.construct_yaml_map(node)
        data_dict = list(data_dict)[0]
        # 遍历dataclass的字段，应用自定义反序列化逻辑
        for field in dataclasses.fields(cls):
            if 'deserialize' in field.metadata:
                deserialize_func = field.metadata['deserialize']
                data_dict[field.name] = deserialize_func(data_dict[field.name])
        # return cls(**data_dict)
        return data_dict

    return config_class_representer, config_class_constructor


class YamlAgent(BasicAgent):
    default_extension = '.yml'

    @staticmethod
    def get_yaml(configuration: Configuration):
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)

        for cls in configuration.all_dataclass:
            if is_config_class(cls):
                # 'tag:yaml.org,2002:map'
                name = cls.__CONF_ROOT__.name
                representer, constructor = make_serializer(cls)
                yaml.representer.add_representer(cls, representer)
                yaml.constructor.add_constructor(f'!{name}', constructor)
            else:  # 就是普通的dataclass
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
        data2obj(instance, data)
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
            data = self.get_yaml(configuration).load(f)
        return data if data is not None else {}

    def load(self, configuration: Configuration, instance):
        BasicAgent.load(self, configuration, instance)
        res = self._load(configuration)
        data = res[configuration.name]
        # 覆盖原instance中的变量
        data2obj(instance, data)
        return instance

    def save(self, configuration: Configuration, instance) -> None:
        BasicAgent.save(self, configuration, instance)
        total_data = self._load(configuration)
        total_data[configuration.name] = instance

        with open(self.location, 'w') as f:
            self.get_yaml(configuration).dump(total_data, f)
