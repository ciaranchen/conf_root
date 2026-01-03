from dataclasses import is_dataclass, MISSING, dataclass, fields as dataclass_fields
from typing import Optional, Type
import logging

from pydantic import create_model, model_validator, Field as PydanticField, BaseModel as PydanticBaseModel
from pydantic._internal._model_construction import ModelMetaclass

from conf_root.agents.BasicAgent import BasicAgent


logger = logging.getLogger(__name__)


def dataclass_to_pydantic(cls: Type, conf_root_instance) -> Type[PydanticBaseModel]:
    """将 dataclass 转换为 Pydantic 模型"""
    if isinstance(cls, PydanticBaseModel) or isinstance(cls, ModelMetaclass):
        return cls
    
    if not is_dataclass(cls):
        cls = dataclass(cls)
    
    fields_dict = {}
    for field in dataclass_fields(cls):
        if field.default is not MISSING:
            fields_dict[field.name] = (field.type, field.default)
        elif field.default_factory is not MISSING:
            fields_dict[field.name] = (field.type, PydanticField(default_factory=field.default_factory))
        else:
            fields_dict[field.name] = (field.type, ...)
    
    return create_model(cls.__name__, **fields_dict)


def create_configuration_class(
    dynamic_model: Type[PydanticBaseModel],
    filename: str,
    conf_root_instance
) -> Type[PydanticBaseModel]:
    """创建配置类"""
    class ConfigurationClass(dynamic_model):
        __CONF_ROOT__ = conf_root_instance
        __CONF_AGENT__ = None
        __CONF_LOCATION__ = filename

        @model_validator(mode='wrap')
        @classmethod
        def check_and_load(cls, param_data, handler):
            if cls.__CONF_AGENT__ and cls.__CONF_AGENT__.exist(cls):
                file_data = cls.__CONF_AGENT__.load(cls)
                if conf_root_instance.priority == 'file':
                    param_data.update(file_data)
                    return handler(param_data)
                else:
                    file_data.update(param_data)
                    return handler(file_data)
            obj = handler(param_data)
            if obj.__CONF_AGENT__:
                obj.__CONF_AGENT__.save(obj)
            return obj

    return ConfigurationClass


def setup_configuration_methods(config_class: Type[PydanticBaseModel], conf_root_instance, filename: str):
    """设置配置类的方法"""
    from functools import update_wrapper
    
    if conf_root_instance.agent_class is not None:
        setattr(config_class, '__CONF_AGENT__', conf_root_instance.agent_class())
        setattr(config_class, '__CONF_LOCATION__', conf_root_instance.agent_class.formalize_filename(filename))

        def save_configuration(_self):
            agent = _self.__CONF_AGENT__
            return agent.save(_self)

        if not hasattr(config_class, 'save_configuration'):
            config_class.save_configuration = save_configuration


def create_config_decorator(conf_root_instance):
    """创建配置装饰器"""
    def decorator(*args, **kwargs):
        def wrapper(cls, filename: Optional[str] = None):
            from functools import update_wrapper
            
            dynamic_model = dataclass_to_pydantic(cls, conf_root_instance)
            
            if filename is None:
                filename = BasicAgent.class_name(cls)
            
            config_class = create_configuration_class(dynamic_model, filename, conf_root_instance)
            update_wrapper(config_class, cls, updated=[])
            
            setup_configuration_methods(config_class, conf_root_instance, filename)
            
            return config_class

        if len(args) == 1 and isinstance(args[0], type):
            # 无参数情况下，相当于直接用类的定义调用decorator.
            # @config
            return wrapper(args[0], **kwargs)
        if len(args) >= 1:
            # 有args的情况下，取第一个args为 config 名称。
            # @config('config'）
            return lambda cls: wrapper(cls, *args, **kwargs)
        return lambda cls: wrapper(cls, **kwargs)

    # 无args, 只有kwargs的情况下，直接给出decorator
    # @config() or @config(name='config')
    return decorator
