# coding:utf-8

'''
注册蓝本认证路由
'''

from flask import Blueprint

auth = Blueprint('auth',__name__)

from . import views
