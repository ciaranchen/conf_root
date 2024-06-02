import os
import ast
import importlib.util
from dataclasses import fields
from typing import Dict, Type

from wtforms.validators import DataRequired, Disabled
from wtforms import Form, StringField, IntegerField, BooleanField, FloatField, TextAreaField, FormField, SelectField, RadioField
from jinja2 import Template
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

from conf_root.Configuration import is_config_class
from conf_root.utils import data2obj


def extract_classes_from_file(file_path):
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
    classes = [cls for cls in classes if cls is not None and is_config_class(cls)]
    return classes


def dataclass_to_wtform(dataclass_type):
    class DynamicForm(Form):
        pass

    for field in fields(dataclass_type):
        field_name = field.name
        field_type = field.type
        field_default = field.default

        # 根据字段类型添加相应的WTForms字段
        if 'choices' in field.metadata:
            choices = field.metadata['choices']
            form_field = RadioField(field_name, choices=choices, validators=[DataRequired()], default=field_default)
        elif field_type == str:
            form_field = StringField(field_name, validators=[DataRequired()], default=field_default)
        elif field_type == int:
            form_field = IntegerField(field_name, validators=[DataRequired()], default=field_default)
        elif field_type == bool:
            form_field = BooleanField(field_name, validators=[DataRequired()], default=field_default)
        elif field_type == float:
            form_field = FloatField(field_name, validators=[DataRequired()], default=field_default)
        elif is_config_class(field_type):
            form_field = FormField(dataclass_to_wtform(field_type), field_name, separator='.')
            pass
        else:
            form_field = TextAreaField(field_name, validators=[Disabled()], default=f"不支持在线编辑类型 {field_type}")
            setattr(DynamicForm, "_" + field_name, form_field)
            continue
        setattr(DynamicForm, field_name, form_field)
    return DynamicForm


def make_handler(forms: Dict[Type, Type]):
    class RequestHandler(BaseHTTPRequestHandler):
        def __init__(self, request, client_address, server):
            self.forms = forms
            super().__init__(request, client_address, server)

        @staticmethod
        def render_index(names):
            urls = [name if name.startswith('/') else '/' + name for name in names]
            template_str = """
            <!doctype html>
            <html>
            <head>
                <title>ConfRoot Form Index</title>
                <meta charset="UTF-8" />
            </head>
            <body>
                <h1>ConfRoot Form Index</h1>
                <ul>
                    {% for name, url in zip(names, urls) %}
                        <li><a href="{{ url }}">{{ name }}</a></li>
                    {% endfor %}
                </ul>
            </body>
            </html>
            """
            template = Template(template_str)
            return template.render(names=names, urls=urls, zip=zip)

        @staticmethod
        def render_form(name, form, action_url):
            template_str = """
            <!doctype html>
            <html>
            <head>
                <title>{{ name }}</title>
                <meta charset="UTF-8" />
            </head>
            <body>
                <h1>{{ name }}</h1>
                <form method="POST" action="{{ action_url }}">
                    {% for field in form %}
                        <p>
                            {{ field.label }}{% if field.flags.required %}*{% endif %}<br>
                            {{ field(size=20) }}<br>
                            {% for error in field.errors %}
                                <span style="color: red;">[{{ error }}]</span><br>
                            {% endfor %}
                        </p>
                    {% endfor %}
                    <p><input type="submit" value="Submit"></p>
                </form>
            </body>
            </html>
            """
            template = Template(template_str)
            return template.render(name=name, form=form, action_url=action_url)

        def do_GET(self):
            if self.path == '/':
                names = [cls.__name__ for cls in self.forms.keys()]
                response = self.render_index(names)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))
                return
            for cls, form_class in self.forms.items():
                name = cls.__name__
                action_url = name if name.startswith('/') else '/' + name
                if self.path == action_url:
                    # 构造Dataclass
                    obj = cls()
                    form = form_class(obj=obj)
                    response = self.render_form(name, form, action_url)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                    return

            # 如果没有匹配的form。
            self.send_response(404)
            self.end_headers()

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = urllib.parse.parse_qsl(post_data.decode('utf-8'))
            post_data = dict(post_data)

            def set_form_data(form_obj, data):
                for field_name, values in data.items():
                    if '.' in field_name:
                        sub_form_name, sub_field_name = field_name.split('.', 1)
                        sub_form = getattr(form_obj, sub_form_name)
                        set_form_data(sub_form, {sub_field_name: values})
                    else:
                        form_obj.process(None, data={field_name: values})

            for cls, form_class in self.forms.items():
                name = cls.__name__
                action_url = name if name.startswith('/') else '/' + name
                if self.path == action_url:
                    form = form_class()
                    set_form_data(form, post_data)
                    if form.validate():
                        # 写入instance
                        instance = cls()
                        data2obj(instance, form.data)
                        configuration = cls.__CONF_ROOT__
                        configuration.conf_root.agent.save(configuration, instance)
                        # 返回结果
                        response = f"Form submitted! Data: {form.data} => {instance}"
                    else:
                        response = self.render_form(name, form, action_url)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.encode('utf-8'))
                    return
            self.send_response(404)
            self.end_headers()

    return RequestHandler


def run_http(forms, host='127.0.0.1', port=8080):
    server_address = (host, port)
    handler_class = make_handler(forms)
    httpd = HTTPServer(server_address, handler_class)
    print(f'Starting httpd server on http://{host}:{port}/ ...')
    httpd.serve_forever()
