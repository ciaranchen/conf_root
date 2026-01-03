import argparse
from typing import Optional, Type, List
import logging

from pydantic import create_model, model_validator, Field as PydanticField


logger = logging.getLogger(__name__)


def get_default(action: argparse.Action):
    """获取 action 的默认值"""
    if action.default and action.default != argparse.SUPPRESS:
        return action.default
    if action.const:
        return action.const
    return None


def get_type(action: argparse.Action):
    """获取 action 的类型"""
    if action.nargs and action.nargs != '?':
        return list
    if action.type is not None:
        return action.type
    default = get_default(action)
    if default:
        return type(default)
    return str


def create_fields_from_parser(parser: argparse.ArgumentParser, skip_dest: Optional[List] = None) -> dict:
    """从 argparse.ArgumentParser 创建 Pydantic 字段"""
    skip_dest = skip_dest if skip_dest is not None else []
    fields = {}
    
    for action in parser._actions:
        name = action.dest
        if name in skip_dest:
            logger.info(f'Skip dest {name} action {action}')
            continue

        field_type = get_type(action)
        if not action.required:
            field_type = Optional[field_type]
        field_default = get_default(action)
        
        logger.debug(action)
        logger.debug(str(field_type) + ' ' + str(field_default))

        if isinstance(action, argparse._HelpAction) or isinstance(action, argparse._VersionAction):
            continue
        elif isinstance(action, argparse._StoreAction) or isinstance(action, argparse._StoreConstAction):
            fields[name] = (field_type, PydanticField(default=field_default, description=action.help))
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
    
    return fields


def create_model_from_parser(
    parser: argparse.ArgumentParser,
    cls_name: str = 'ArgparseConfig',
    skip_dest: Optional[List] = None
) -> Type:
    """从 argparse.ArgumentParser 创建 Pydantic 模型"""
    fields = create_fields_from_parser(parser, skip_dest)
    return create_model(cls_name, __doc__=parser.description, **fields)
