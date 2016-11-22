# coding=utf-8
from . import db
from flask import current_app
from . import login_manager
from flask_login import UserMixin, AnonymousUserMixin
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean(),default=False,index=True)
    permissions=db.Column(db.Integer)
    # 一个角色可以属于多个用户
    # 加入lazy参数以便更好添加过滤器
    user = db.relationship('User',backref='role',lazy='dynamic')


    @staticmethod
    def insert_role():
        roles = {
            'User' : (Permission.FOLLOW |
                      Permission.COMMENT |
                      Permission.WRITE_ARTICLES, True),

            'Moderate' : (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator' : (0xff,False)

        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions=roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
            db.session.commit()

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

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['BLOGER_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

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

    def can(self,permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User % r>' % self.username

class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user=AnonymousUserMixin

# 创建一个回调函数以使用指定标识符加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



