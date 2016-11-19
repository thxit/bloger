# coding=utf-8

from flask import Flask, render_template, url_for, session, redirect, flash
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

def current_app(config_name):
    app =Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

# 利用了一个装饰器来初始化对象
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

