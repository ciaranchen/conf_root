from typing import Dict, Type
import urllib.parse
from jinja2 import Template
from http.server import BaseHTTPRequestHandler, HTTPServer


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
                    # TODO: 处理递归的情况。
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

            for cls, form_class in self.forms.items():
                name = cls.__name__
                action_url = name if name.startswith('/') else '/' + name
                if self.path == action_url:
                    form = form_class(data=post_data)
                    if form.validate():
                        response = f"Form submitted! Data: {form.data}"
                        # 写入instance
                        instance = cls()
                        for k, v in form.data.items():
                            setattr(instance, k, v)
                        print(instance)
                        configuration = cls.__CONF_ROOT__
                        configuration.conf_root.agent.save(configuration, instance)
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
