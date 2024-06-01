from dataclasses import fields
from wtforms import Form, StringField, IntegerField, BooleanField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Disabled


def dataclass_to_wtform(dataclass_type):
    class DynamicForm(Form):
        pass

    for field in fields(dataclass_type):
        field_name = field.name
        field_type = field.type
        field_default = field.default

        # TODO: 处理迭代问题
        # 根据字段类型添加相应的WTForms字段
        if field_type == str:
            form_field = StringField(field_name, validators=[DataRequired()], default=field_default)
        elif field_type == int:
            form_field = IntegerField(field_name, validators=[DataRequired()], default=field_default)
        elif field_type == bool:
            form_field = BooleanField(field_name, validators=[DataRequired()], default=field_default)
        elif field_type == float:
            form_field = FloatField(field_name, validators=[DataRequired()], default=field_default)
        else:
            form_field = TextAreaField(field_name, validators=[Disabled()], default=f"不支持在线编辑类型 {field_type}")
            setattr(DynamicForm, "<" + field_name, form_field)
            continue
        setattr(DynamicForm, field_name, form_field)
    return DynamicForm
