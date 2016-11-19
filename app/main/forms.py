# coding=utf-8
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(Form):
    name = StringField('你的名字是?', validators=[DataRequired()])
    submit = SubmitField('确定')