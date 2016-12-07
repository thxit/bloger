# coding=utf-8
from . import db
import hashlib,bleach
from flask import request
from flask import current_app
from flask_moment import datetime
from markdown import markdown
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

# 多对多的关联表
class Follow(db.Model):
    __tables__ = 'follows'
    followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # 每个用户只能有一个角色
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    avatar_hash=db.Column(db.String(64))
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    followed = db.relationship('Follow',
                               # 使用指定外键消除歧义
                               foreign_keys =[Follow.follower_id],
                               backref=db.backref('follower',lazy='joined'),
                               lazy = 'dynamic',
                               cascade = 'all, delete-orphan'
                               )
    followers = db.relationship('Follow',
                                foreign_keys = [Follow.followed_id],
                                backref= db.backref('followed',lazy='joined'),
                                lazy = 'dynamic',
                                cascade ='all, delete-orphan'
                                )




    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['BLOGER_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

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

    # 刷新用户的最后访问时间
    def ping(self):
        self.last_seen=datetime.utcnow()
        db.session.add(self)

    def gravatar(self,size=100,default='identicon',rating='g',):
        if request.is_secure:
            url="https://secure.gravatar.com/avatar"
        else:
            url="http://cn.gravatar.com/avatar"
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,size=size,rating=rating,default=default,hash=hash)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username = forgery_py.internet.user_name(True),
                     password = forgery_py.lorem_ipsum.word(),
                     name = forgery_py.name.full_name(),
                     location = forgery_py.address.city(),
                     about_me = forgery_py.lorem_ipsum.sentence(),
                     member_since = forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self,followed=user)
            db.session.add(f)

    def unfollow(self,user):
        f=self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    # 获取所关注用户的文章
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id==Post.author_id)\
            .filter(Follow.follower_id == self.id)



    def __repr__(self):
        return '<User % r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user= AnonymousUser

# 创建一个回调函数以使用指定标识符加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    @staticmethod
    def generate_fake(count=100):
        from random import randint,seed
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0,user_count-1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_change_body(target,value,oldvalue,initiator):
        allowed_tags =['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                       'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                       'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value,out_format='html'),
            tags=allowed_tags,strip=True)
        )

db.event.listen(Post.body, 'set', Post.on_change_body)







