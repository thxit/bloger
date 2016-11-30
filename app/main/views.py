#!usr/bin/env python
#coding:utf-8
from flask import render_template,abort,flash,redirect,url_for
from flask_login import login_required, current_user
from . import main
from ..models import User,Role,db, Permission,Post
from .forms import EditProfileForm, PostForm


@main.route('/', methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
        form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form,posts=posts)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        abort(404)
    posts =user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',user=user,posts=posts)


@main.route('/edit-profile',methods=['GET','POST'])
#@login_required
def edit_profile():
    form=EditProfileForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        flash('你的资料页面已经更新')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',form=form)









