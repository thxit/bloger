#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, render_template, url_for, session, redirect, flash
from flask_script import Manager, Shell
from flask_moment import Moment
from datetime import datetime
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread
import os

app = Flask(__name__)
manager = Manager(app)
moment = Moment(app)
bootstrap = Bootstrap(app)

app.config.from_object(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
# 设置为True时，每次请求结束后自动提交数据库改动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)
migrate = Migrate(app,db)
app.config['SECRET_KEY'] = 'hard to guess'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 配置邮件信息
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL']= False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = 'obkmslncckjaeiac'
app.config['BLOGER_MAIL_SUBJECT_PREFIX']='[Bloger]'
app.config['BLOGER_MAIL_SENDER'] = os.environ.get('BLOGER_MAIL_SENDER')
app.config['BLOGER_ADMIN'] = os.environ.get('BLOGER_ADMIN')
# mail应该放到config后面，不然会报拒绝连接的错误
mail = Mail(app)


class NameForm(Form):
    name = StringField('你的名字是?',validators=[DataRequired()])
    submit = SubmitField('确定')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # 一个角色可以属于多个用户
    # 加入lazy参数以便更好添加过滤器
    user = db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role % r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # 每个用户只能有一个角色
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User % r>' % self.username


@app.route('/', methods = ['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            #if app.config['BLOGER_ADMIN']:
            send_email(app.config['BLOGER_ADMIN'],'New User',
                'mail/new_user', user=user)
            flash('邮件已发送')
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',
        form=form, name=session.get('name'),
        known=session.get('known', False))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


def send_email(to,subject,template,**kwargs):
    msg = Message(app.config['BLOGER_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['BLOGER_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    mail.send(msg)

# 异步发送电子邮件
def send_async_email(app,msg):
    with app.app_context():
        send_email(msg)


def make_shell_context():    # 将对象添加到导入列表中并且自动导入
    return dict(app=app,db=db,User=User,Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)





if __name__ == '__main__':
    manager.run()
