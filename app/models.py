# coding=utf-8
from . import db
from . import login_manager
from flask_login import UserMixin
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # 一个角色可以属于多个用户
    # 加入lazy参数以便更好添加过滤器
    user = db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role % r>' % self.name


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # 每个用户只能有一个角色
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('此密码不可读')

    # 原始密码输入，字符串散列值输出保存于数据库
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    # 从数据库中取出密码的散列值和用户的输入密码
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return '<User % r>' % self.username

# 创建一个回调函数以使用指定标识符加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



