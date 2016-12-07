#!usr/bin/env python
#coding:utf-8
from flask import render_template,abort,flash,redirect,url_for,request,current_app,make_response
from flask_login import login_required, current_user
from . import main
from ..models import User,Role,db, Permission,Post
from .forms import EditProfileForm, PostForm
from ..decorators import admin_required, permission_required



@main.route('/', methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
        form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    # 分页显示博客文章列表
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGER_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form,posts=posts,
                           pagination = pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['BLOGER_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html',user=user,posts=posts,pagination=pagination)


@main.route('/edit-profile',methods=['GET','POST'])
@login_required
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

# 文章固定链接
@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])

# 编辑博客文章的路由
@main.route('/edit/<int:id>',methods=['GET','POST'])
def edit(id):
    post = Post.query.get_or_404(id)
    # 管理员例外
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('文章已经更改')
        redirect(url_for('.post', id=post.id))
    form.body.data=post.body
    return render_template('edit_post.html',form=form)


@main.route('/follow/<username>')
@permission_required(Permission.FOLLOW)
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在此用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注了此用户')
        return redirect(url_for('.user'))
    current_user.follow(user)
    flash('你已成功关注 %s' % username)
    return redirect(url_for('.user',username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在此用户')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你还未关注该用户')
    current_user.unfollow(user)
    flash('你已经成功取消关注')
    return redirect(url_for('.user',username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['BLOGER_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',user=user,title='的粉丝',endpoint='.followers',
                           pagination=pagination,follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['BLOGER_FOLLOWERS_PER_PAGE'],
        error_out=False
    )
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',user=user,title='关注的人',endpoint='.followed_by',
                           pagination=pagination,follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp








