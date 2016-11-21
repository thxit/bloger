# coding:utf-8
from . import auth
from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, logout_user, current_user,login_required
from .forms import LoginForm,RegistrationForm
from ..models import User
from .. import db

@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # Flask-Login会把原地址保存在查询字符串的 next 参数中
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('无效的用户名或密码')
    return render_template('auth/login.html',form=form)

@auth.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('你已经退出界面')
    return redirect(url_for('main.index'))


@auth.route('/register',method=['GET','POST'])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username = form.username.data,
                    password = form.password.data)
        db.session.add(user)
        flash('你已经可以登录了')
        redirect(url_for('auth.login'))
    return render_template('auth/register',form=form)
