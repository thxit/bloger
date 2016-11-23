#coding:utf-8
'''

'''
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Length, Email, DataRequired, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email=StringField('邮箱',validators=[DataRequired(), Length(1,64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(Form):
    email = StringField('邮箱',validators=[DataRequired(),Length(1,64), Email()])
    username = StringField('账号',validators=[DataRequired(), Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                                                                  '账户名不能为空')])
    password = PasswordField('密码', validators =[
        DataRequired(), EqualTo('password2',message='密码必须匹配')])
    password2 = PasswordField('确定密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            return ValidationError('邮箱已被注册')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            return ValidationError('账户名已被使用')


