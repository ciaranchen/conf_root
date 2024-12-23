import dataclasses
import os
import re

from ruamel.yaml import CommentedMap
from dataclasses import is_dataclass, fields


def all_dataclass(_class):
    def _recursive_dataclass(cls):
        if is_dataclass(cls):
            return sum([_recursive_dataclass(field.type) for field in fields(cls)], [cls])
        return []

    return _recursive_dataclass(_class)


def formalize_filename(name):
    invalid_chars_pattern = r'[\\/:*?"<>|]'
    filename = re.sub(invalid_chars_pattern, '_', name)
    return filename


def ensure_suffix(path, default_extension):
    # 检查文件路径是否已经有后缀名
    _, ext = os.path.splitext(path)
    # 如果后缀名不为空并且不是我们要添加的后缀名（考虑大小写）
    if ext.lower() != default_extension.lower():
        # 如果没有后缀名或者后缀名不同，则添加后缀名
        # 注意：这里使用os.path.basename来获取文件名，然后再拼接新的文件名和目录
        directory, filename = os.path.split(path)
        new_filename = filename + default_extension
        new_path = os.path.join(directory, new_filename)
        return new_path
    else:
        # 如果后缀名已经存在或者文件路径没有后缀名（即ext为空），则直接返回原路径
        return path


def make_serializer(cls):
    name = cls.__CONF_ROOT__.class_name(cls)

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
        for field in fields(cls):
            if 'deserialize' in field.metadata:
                deserialize_func = field.metadata['deserialize']
                data_dict[field.name] = deserialize_func(data_dict[field.name])
        # return cls(**data_dict)
        return data_dict

    return config_class_representer, config_class_constructor
