from typing import Optional, Type, Literal
import logging
import argparse

from conf_root.agents.BasicAgent import BasicAgent
from conf_root.agents.YamlAgent import YamlAgent
from conf_root.run_http import run_http, extract_classes_from_file
from conf_root.config_decorator import create_config_decorator
from conf_root.argparse_converter import create_model_from_parser
from conf_root.utils import is_config_class


logger = logging.getLogger(__name__)


class ConfRoot:
    def __init__(self, agent_class: Optional[Type[BasicAgent]] = YamlAgent,
                 priority: Literal['file', 'param'] = 'file'):
        self.agent_class = agent_class
        self.priority = priority

    def config(self, *args, **kwargs):
        return create_config_decorator(self)(*args, **kwargs)

    @staticmethod
    def is_config_class(cls_or_instance):
        return is_config_class(cls_or_instance)

    def from_argparse(self, parser, cls_name: str = 'ArgparseConfig', *args,
                      skip_dest: Optional[list] = None, **kwargs):
        from functools import update_wrapper
        from pydantic import model_validator
        
        DynamicModel = create_model_from_parser(parser, cls_name, skip_dest)
        ConfigModel = self.config(DynamicModel, *args, **kwargs)

        class HandleSkip(ConfigModel):
            @model_validator(mode='wrap')
            @classmethod
            def skip_destination(cls, data, handler):
                skip_dest_list = skip_dest if skip_dest is not None else []
                data = {k: v for k, v in data.items() if k not in skip_dest_list}
                return handler(data)

        update_wrapper(HandleSkip, DynamicModel, updated=[])
        return HandleSkip

    @staticmethod
    def serve(classes, host='127.0.0.1', port=8080):
        run_http({cls: cls for cls in classes}, host=host, port=port)


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
