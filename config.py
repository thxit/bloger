#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# 设定多个数据库配置
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'hard to guess'

    # 设置为True时，每次请求结束后自动提交数据库改动
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    BLOGER_MAIL_SUBJECT_PREFIX = '[Bloger]'
    BLOGER_MAIL_SENDER = os.environ.get('BLOGER_MAIL_SENDER')
    BLOGER_ADMIN = os.environ.get('BLOGER_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = 'obkmslncckjaeiac'
    BLOGER_POSTS_PER_PAGE = 20

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')



class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'testing':TestingConfig,

    'default':DevelopmentConfig
}