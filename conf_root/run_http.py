from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from jinja2 import Template
from wtforms import Form, StringField, IntegerField, BooleanField, FloatField
from wtforms.validators import DataRequired


class Form1(Form):
    username = StringField('Username', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])


class Form2(Form):
    email = StringField('Email', validators=[DataRequired()])
    score = FloatField('Score', validators=[DataRequired()])


class RequestHandler(BaseHTTPRequestHandler):

    def render_index(self):
        template_str = """
        <!doctype html>
        <html>
        <head>
            <title>Multiple WTForms Example</title>
        </head>
        <body>
            <h1>Form Index</h1>
            <ul>
                <li><a href="/form1">Form 1</a></li>
                <li><a href="/form2">Form 2</a></li>
            </ul>
        </body>
        </html>
        """
        template = Template(template_str)
        return template.render()

    def render_form(self, form, action_url):
        template_str = """
        <!doctype html>
        <html>
        <head>
            <title>Multiple WTForms Example</title>
        </head>
        <body>
            <h1>Multiple WTForms Example</h1>
            <form method="POST" action="{{ action_url }}">
                {{ form.hidden_tag() }}
                {% for field in form %}
                    <p>
                        {{ field.label }}<br>
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
        return template.render(form=form, action_url=action_url)

    def do_GET(self):
        if self.path == '/':
            response = self.render_index()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        elif self.path == '/form1':
            form = Form1()
            action_url = '/form1'
            response = self.render_form(form, action_url)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        elif self.path == '/form2':
            form = Form2()
            action_url = '/form2'
            response = self.render_form(form, action_url)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = urllib.parse.parse_qs(post_data.decode('utf-8'))

        if self.path == '/form1':
            form = Form1(data=post_data)
            action_url = '/form1'
        elif self.path == '/form2':
            form = Form2(data=post_data)
            action_url = '/form2'
        else:
            self.send_response(404)
            self.end_headers()
            return

        if form.validate():
            response = f"Form submitted! Data: {form.data}"
        else:
            response = self.render_form(form, action_url)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()


if __name__ == "__main__":
    run()
