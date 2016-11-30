# coding=utf-8
from flask_wtf import Form
from wtforms import StringField, SubmitField,TextAreaField, SelectField
from wtforms.validators import DataRequired,Length
from flask_pagedown.fields import PageDownField


class NameForm(Form):
    name = StringField('你的名字是?', validators=[DataRequired()])
    submit = SubmitField('确定')


class EditProfileForm(Form):
    name = StringField('姓名',validators=[Length(0,64)])
    location = StringField('地址',validators=[DataRequired()])
    about_me = TextAreaField('个人介绍')
    submit = SubmitField('确定')


class PostForm(Form):
    body = PageDownField('你想写点什么吗？',validators=[DataRequired()])
    submit = SubmitField('确定')