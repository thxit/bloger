#coding:utf-8
from flask import Blueprint

main = Blueprint('main',__name__)

from . import errors, views
from ..models import Permission


#把Permission类加入全局上下文
@main.app_context_processor
def inject_permisssions():
    return dict(Permission=Permission)