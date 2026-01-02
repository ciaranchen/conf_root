import os
import ast
import importlib.util
from typing import Dict, Type, Any, List, get_origin, get_args
from pydantic import BaseModel, ValidationError

import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer


def extract_classes_from_file(file_path):
    from conf_root.ConfRoot import ConfRoot
    
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    classes_name = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    # Dynamically import the module
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Load the classes from the module
    classes = [getattr(module, class_name, None) for class_name in classes_name]
    classes = [cls for cls in classes if cls is not None and ConfRoot.is_config_class(cls)]
    return classes


def get_field_info(field_name: str, field_info: Any) -> Dict[str, Any]:
    """获取字段的元数据信息"""
    field_type = field_info.annotation
    field_default = field_info.default
    
    # 处理可选类型
    is_optional = field_info.is_required
    
    # 获取字段默认值
    default_value = None
    if default_value is None and hasattr(field_info, 'default'):
        default_value = field_info.default
    if default_value is None and hasattr(field_default, 'default_factory'):
        default_value = field_default.default_factory()

    # 获取类型名称
    type_name = None
    if hasattr(field_type, '__name__'):
        type_name = field_type.__name__
    elif hasattr(field_type, '_name'):
        type_name = field_type._name
    
    return {
        'name': field_name,
        'type': type_name,
        'annotation': field_type,
        'is_optional': is_optional,
        'default': default_value,
        'is_required': not is_optional and default_value is None
    }


def get_model_fields(model_type: Type[BaseModel]) -> List[Dict[str, Any]]:
    """获取 Pydantic 模型的所有字段信息"""
    from conf_root.ConfRoot import ConfRoot
    
    fields_info = []
    for field_name, field_info in model_type.model_fields.items():
        field_data = get_field_info(field_name, field_info)
        
        # 检查是否是嵌套的配置类
        if ConfRoot.is_config_class(field_info.annotation):
            field_data['is_nested'] = True
            field_data['nested_fields'] = get_model_fields(field_info.annotation)
        else:
            field_data['is_nested'] = False
        
        fields_info.append(field_data)
    
    return fields_info


def make_handler(models: Dict[Type, Type]):
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError as e:
        missing_lib = str(e).split("'")[1]
        print(f"错误: 缺少必要的依赖库 '{missing_lib}'")
        print("请使用以下命令安装 web 依赖:")
        print("  pip install conf_root[web]")
        print("或者:")
        print("  pip install jinja2")
        exit(1)

    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self, request, client_address, server):
            self.models = models
            template_path = os.path.join(os.path.dirname(__file__), 'templates')
            self.jinja_env = Environment(loader=FileSystemLoader(template_path))
            super().__init__(request, client_address, server)

        def render_index(self, names):
            urls = [name if name.startswith('/') else '/' + name for name in names]
            template = self.jinja_env.get_template('index.html')
            return template.render(names=names, urls=urls, zip=zip)

        def render_form(self, name, model, fields, action_url, msg=None, errors=None):
            template = self.jinja_env.get_template('form.html')
            return template.render(
                name=name,
                model=model,
                fields=fields,
                action_url=action_url,
                msg=msg,
                errors=errors or {}
            )

        def do_GET(self):
            if self.path == '/':
                names = [cls.__name__ for cls in self.models.keys()]
                response = self.render_index(names)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))
                return
            
            for model in self.models.keys():
                name = model.__name__
                action_url = name if name.startswith('/') else '/' + name
                if self.path == action_url:
                    # 获取模型实例和字段信息
                    obj = model()
                    fields = get_model_fields(model)
                    response = self.render_form(name, obj, fields, action_url)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                    return

            # 如果没有匹配的模型
            self.send_response(404)
            self.end_headers()

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = urllib.parse.parse_qsl(post_data.decode('utf-8'))
            post_data = dict(post_data)

            def parse_value(field_info, value):
                """根据字段类型解析值"""
                field_type = field_info['type']
                if field_type == 'int':
                    return int(value) if value else None
                elif field_type == 'float':
                    return float(value) if value else None
                elif field_type == 'bool':
                    return value == 'true' or value == 'on'
                else:
                    return value

            def build_model_data(model_type, data, prefix=''):
                """递归构建模型数据"""
                model_data = {}
                fields_info = get_model_fields(model_type)
                
                for field_info in fields_info:
                    field_name = field_info['name']
                    full_name = f"{prefix}{field_name}" if prefix else field_name
                    
                    if field_info['is_nested']:
                        # 处理嵌套模型
                        nested_data = build_model_data(field_info['annotation'], data, f"{field_name}.")
                        model_data[field_name] = nested_data
                    else:
                        # 处理普通字段
                        value = data.get(full_name, field_info['default'])
                        model_data[field_name] = parse_value(field_info, value)
                
                return model_data

            for model in self.models.keys():
                name = model.__name__
                action_url = name if name.startswith('/') else '/' + name
                if self.path == action_url:
                    fields = get_model_fields(model)
                    
                    try:
                        # 构建模型数据
                        model_data = build_model_data(model, post_data)
                        
                        # 创建并验证模型实例
                        instance = model(**model_data)
                        
                        # 保存配置
                        agent = model.__CONF_AGENT__
                        agent.save(instance)
                        
                        # 返回成功消息
                        conf_location = model.__CONF_LOCATION__
                        msg = {
                            'location': agent.formalize_filename(conf_location),
                            'data': model_data,
                            'instance': instance
                        }
                        response = self.render_form(name, instance, fields, action_url, msg=msg)
                    except ValidationError as e:
                        # 处理验证错误
                        errors = {}
                        for error in e.errors():
                            field_name = '.'.join(str(loc) for loc in error['loc'])
                            errors[field_name] = error['msg']
                        
                        response = self.render_form(name, model(**model_data), fields, action_url, errors=errors)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                    return
            
            self.send_response(404)
            self.end_headers()

    return RequestHandler


def run_http(models, host='127.0.0.1', port=8080):
    server_address = (host, port)
    handler_class = make_handler(models)
    httpd = HTTPServer(server_address, handler_class)
    print(f'Starting httpd server on http://{host}:{port}/ ...')
    httpd.serve_forever()
