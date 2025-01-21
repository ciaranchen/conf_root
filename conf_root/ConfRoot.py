import argparse
from dataclasses import is_dataclass, MISSING, dataclass, field as dataclass_field, fields as dataclass_fields
from functools import update_wrapper
from typing import Optional, Type, List
import logging

from pydantic import create_model, model_validator, Field as PydanticField, BaseModel as PydanticBaseModel

from conf_root.agents.BasicAgent import BasicAgent
from conf_root.agents.YamlAgent import SingleFileYamlAgent
from conf_root.run_http import run_http, extract_classes_from_file, dataclass_to_wtform


logger = logging.getLogger(__name__)


class ConfRoot:
    def __init__(self, agent_class: Optional[Type[BasicAgent]] = SingleFileYamlAgent):
        self.agent_class = agent_class

    def config(self, *args, **kwargs):
        def decorator(cls, filename: Optional[str] = None):
            if isinstance(cls, PydanticBaseModel):
                DynamicModel = cls
            else:
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
                        # TODO: 给出可修改的选项；作为ConfRoot的变量。
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

    def from_argparse(self, parser: argparse.ArgumentParser, cls_name: str = 'ArgparseConfig',
                      skip_dest: Optional[List] = None):
        def get_default(action):
            if action.default and action.default != argparse.SUPPRESS:
                return action.default
            if action.const and isinstance(action, argparse._StoreConstAction):
                return action.const

        def get_type(action):
            if action.nargs and action.nargs != '?':
                return List
            # 如果有指定的type，直接使用指定的type
            if action.type is not None:
                return action.type
            # 如果有default，则以default的类型优先
            default = get_default(action)
            if default:
                return type(default)
            return str

        skip_dest = skip_dest if skip_dest is not None else []
        fields = {}
        for action in parser._actions:
            name = action.dest
            if name in skip_dest:
                logger.info(f'Skip dest {name} action {action}')

            # TODO: 使用try catch处理，添加为skip_dest.
            field_type = get_type(action)
            field_default = get_default(action)
            # print(action)
            # print(field_type, field_default)

            if isinstance(action, argparse._HelpAction) or isinstance(action, argparse._VersionAction):
                continue
            elif isinstance(action, argparse._StoreAction):
                fields[name] = (field_type, PydanticField(default=field_default, description=action.help))
            elif isinstance(action, argparse._StoreConstAction):
                fields[name] = (type(action.const), action.const)
            elif isinstance(action, argparse._StoreTrueAction) or isinstance(action, argparse._StoreFalseAction):
                fields[name] = (bool, action.const)
            elif (isinstance(action, argparse._AppendAction) or isinstance(action, argparse._AppendConstAction)
                  or isinstance(action, argparse._ExtendAction)):
                fields[name] = (List, PydanticField(default=field_default, description=action.help))
            elif isinstance(action, argparse._CountAction):
                fields[name] = (int, PydanticField(default=field_default, description=action.help))
            elif isinstance(action, argparse.BooleanOptionalAction):
                fields[name] = (bool, PydanticField(default=field_default, description=action.help))
            else:
                skip_dest.append(name)
                logger.warning(f'Skiped Argparse: {action.dest} action {action.__class__.__name__}')
                continue
        cls = create_model(cls_name, **fields)
        DynamicModel = self.config(cls)

        class HandleSkip(DynamicModel):
            @model_validator(mode='wrap')
            @classmethod
            def skip_destination(cls, data, handler):
                data = {k: v for k, v in data.items() if k not in skip_dest}
                return handler(data)

        update_wrapper(HandleSkip, DynamicModel, updated=[])
        return HandleSkip

    @staticmethod
    def serve(classes, host='127.0.0.1', port=8080):
        forms = {cls: dataclass_to_wtform(cls) for cls in classes}
        run_http(forms, host=host, port=port)


def main():
    parser = argparse.ArgumentParser(prog='conf-root-web',
                                     description="这个脚本允许您在一个网页中可视化地修改您的配置文件。")
    parser.add_argument('filename', help="提取配置类的Python文件名")
    parser.add_argument('--host', '-H', default='127.0.0.1', help='服务器的host')
    parser.add_argument('--port', '-P', default=8080, help='服务器的port')
    args = parser.parse_args()

    classes = extract_classes_from_file(args.filename)
    if len(classes) == 0:
        print(f"No classes found in {args.filename}.")
        return
    print(f"Configuration classes defined in {args.filename}: {classes}")
    ConfRoot.serve(classes, args.host, args.port)


if __name__ == "__main__":
    main()
