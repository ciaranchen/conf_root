from dataclasses import fields
from wtforms import Form, StringField, IntegerField, BooleanField, FloatField
from wtforms.validators import DataRequired


def dataclass_to_wtform(dataclass_type):
    class DynamicForm(Form):
        pass

    for field in fields(dataclass_type):
        field_name = field.name
        field_type = field.type

        # 根据字段类型添加相应的WTForms字段
        if field_type == str:
            setattr(DynamicForm, field_name, StringField(field_name.capitalize(), validators=[DataRequired()]))
        elif field_type == int:
            setattr(DynamicForm, field_name, IntegerField(field_name.capitalize(), validators=[DataRequired()]))
        elif field_type == bool:
            setattr(DynamicForm, field_name, BooleanField(field_name.capitalize()))
        elif field_type == float:
            setattr(DynamicForm, field_name, FloatField(field_name.capitalize(), validators=[DataRequired()]))
    return DynamicForm
