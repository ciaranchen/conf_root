import argparse
from dataclasses import make_dataclass, is_dataclass, MISSING, dataclass, field as dataclass_field, \
    fields as dataclass_fields
from functools import update_wrapper
from typing import Optional, Type, List
import logging

from pydantic import create_model, model_validator

from conf_root.agents.BasicAgent import BasicAgent
from conf_root.agents.YamlAgent import SingleFileYamlAgent

logger = logging.getLogger(__name__)


class ConfRoot:
    def __init__(self, agent_class: Optional[Type[BasicAgent]] = SingleFileYamlAgent):
        self.agent_class = agent_class

    def config(self, *args, **kwargs):
        def decorator(cls, filename: Optional[str] = None):
            if not is_dataclass(cls):
                cls = dataclass(cls)
            DynamicModel = create_model(
                cls.__name__,
                **{field.name: (field.type, field.default) if field.default is not MISSING else (field.type, ...)
                   for field in dataclass_fields(cls)}
            )
            if filename is None:
                filename = self.class_name(cls)

            class ConfigurationClass(DynamicModel):
                __CONF_ROOT__ = self
                __CONF_AGENT__ = None
                __CONF_LOCATION__ = filename

                @model_validator(mode='wrap')
                @classmethod
                def check_and_load(cls, data, handler):
                    # 如果存在，读取和实例化
                    if cls.__CONF_AGENT__ and cls.__CONF_AGENT__.exist(cls):
                        load_data = cls.__CONF_AGENT__.load(cls)
                        # load_data 更优先
                        data.update(load_data)
                    return handler(data)

                @model_validator(mode='after')
                def post_init(_self):
                    if _self.__CONF_AGENT__:
                        _self.__CONF_AGENT__.save(_self)
                    return _self

            # 避免在Configuration的__dict__原本类的 __dict__ 上进行更新。
            update_wrapper(ConfigurationClass, cls, updated=[])
            if self.agent_class is not None:
                setattr(ConfigurationClass, '__CONF_AGENT__', self.agent_class())
                setattr(ConfigurationClass, '__CONF_LOCATION__', self.agent_class.formalize_filename(filename))

                # 设置保存方法
                def save_configuration(_self):
                    agent = _self.__CONF_AGENT__
                    return agent.save(_self)

                ConfigurationClass.save_configuration = save_configuration
            return ConfigurationClass

        if len(args) == 1 and isinstance(args[0], type):
            # 无参数情况下，相当于直接用类的定义调用decorator.
            # @wrap
            return decorator(args[0], **kwargs)
        if len(args) >= 1:
            # 有args的情况下，取第一个args为 config 名称。
            # @wrap('config'）
            return lambda cls: decorator(cls, *args, **kwargs)
        # 无args, 只有kwargs的情况下，直接给出decorator
        # @wrap() or @wrap(name='config')
        return lambda cls: decorator(cls, **kwargs)

    @staticmethod
    def class_name(cls):
        return SingleFileYamlAgent.class_name(cls)

    @staticmethod
    def is_config_class(cls_or_instance):
        return getattr(cls_or_instance, '__CONF_ROOT__', None) is not None

    def from_argparse(self, parser: argparse.ArgumentParser, cls_name: str = 'ArgparseConfig'):
        def get_default(action):
            if action.default and action.default != argparse.SUPPRESS:
                return action.default
            if action.const and isinstance(action, argparse._StoreConstAction):
                return action.const
            # 如果是Required的话，那么传入的参数中必定有它，所以不必有default。
            return MISSING if action.required else None  # 实在没有default的话，就先给None了

        def get_type(action):
            if action.type:
                return action.type
            if action.nargs and action.nargs != '?':
                return List
            if (isinstance(action, argparse._AppendAction) or
                    isinstance(action, argparse._AppendConstAction) or isinstance(action, argparse._ExtendAction)):
                return List
            default = get_default(action)
            if default:
                return type(default)

        def default_field(action):
            metadata = {'validators': []}
            if action.help:
                metadata['comment'] = action.help
            # validators
            if action.choices:
                metadata['validators'].append(lambda x: x in action.choices)
                metadata['choices'] = action.choices
            if action.nargs:
                if isinstance(action.nargs, int):
                    metadata['validators'].append(lambda x: len(x) == action.nargs)
                if action.nargs == '+':
                    metadata['validators'].append(lambda x: len(x) > 0)
            return dataclass_field(default=get_default(action), metadata=metadata)

        fields = []
        for action in parser._actions:
            name = action.dest
            if isinstance(action, argparse._HelpAction) or isinstance(action, argparse._VersionAction):
                continue
            _SUPPORT_ACTIONS = [
                argparse._AppendAction, argparse._AppendConstAction, argparse._CountAction, argparse._ExtendAction,
                argparse._StoreAction, argparse._StoreConstAction, argparse._StoreFalseAction, argparse._StoreTrueAction
            ]
            if not any([isinstance(action, sa) for sa in _SUPPORT_ACTIONS]):
                logger.warning(f'Skiped Argparse: {action.dest} action {action.__class__.__name__}')
                # 暂不考虑不支持的action
                continue
            # TODO: handle other Action.

            _type = get_type(action)
            field = (name, _type, default_field(action))
            fields.append(field)
            # print(field)

        fields = sorted(fields, key=lambda x: x[2].default == MISSING, reverse=True)

        cls = make_dataclass(cls_name, fields)
        return self.config(cls)
