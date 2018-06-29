# encoding=utf-8
from datetime import datetime
from flask import render_template,session,redirect,url_for,abort,flash
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm,PostForm
from  app.auth.forms import LoginForm
from flask_login import  login_required,current_user,login_user
from  flask import request
from .. import db
from app.models import Role,User
from ..models import User,Permission,Post
from ..decorators import admin_required
import sys
sys.setrecursionlimit(10**5)
@main.route('/',methods=['POST','GET'])
@login_required
def index():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return render_template('user.html',user=user)
        flash(u'无效的用户名或密码！')
        return redirect(url_for('main.index'))
    # return render_template('auth/login.html',form=form)
    # return render_template('index.html',form=form,name=session.get('name'),known=session.get('known',False),current_time=datetime.utcnow())
    page=request.args.get('page',1,type=int)
    pagination=Post.query.order_by(Post.timestamp.desc()).paginate(page,per_page=5,error_out=False)
    posts=pagination.items
    return render_template('index.html',form=form,posts=posts,pagination=pagination)
# @main.route('/user/<username>')
# @login_required
# def user(username):
#     user=User.query.filter_by(username=username).first()
#     if user is None:
#         abort(404)
#     return render_template(('user.html'),user=user)
@main.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form=EditProfileForm()
    if form.validate_on_submit():
        current_user.name=form.name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        flash(u'用户名已经使用!!!')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('edit-profile.html',form=form)
@main.route('/edit_profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user=User.query.get_or_404(id)
    form=EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email=form.email.data
        user.username=form.username.data
        user.confirmed=form.confirmed.data
        user.role=Role.query.get(form.role.data)
        user.name=form.name.data
        user.location=form.location.data
        user.about_me=form.about_me.data
        db.session.add(user)
        flash(u'管理员信息已经更新!!!')
        return redirect(url_for('.user',username=user.username))
    form.email.data=user.email
    form.username.data=user.username
    form.confirmed.data=user.confirmed
    form.role.data=user.role_id
    form.name.data=user.name
    form.location.data=user.location
    form.about_me.data=user.about_me
    return render_template('edit-profile.html',form=form,user=user)
@main.route('/post',methods=['POST','GET'])
def post():
    form=PostForm()
    if current_user.can(Permission.WTRITE_ARTICLES) and form.validate_on_submit():
        post=Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    posts=Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html',form=form,posts=posts)
@main.route('/user/<username>',methods=['GET','POST'])
# @login_required
def user(username):
    user=User.query.filter_by(username=username).first()
    print user
    page=request.args.get('page',1,type=int)
    posts=user.posts.order_by(Post.timestamp.desc()).all()
    for post in posts:
        print post
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate( page,per_page=5,error_out=False)
    if user is None:
        abort(404)
    posts=pagination.items
    return  render_template('user.html',user=user,posts=posts,pagination=pagination)
@main.route('/post/<int:id>')
def post_id(id):
    post=Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])
@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post=Post.query.get_or_404(id)
    if current_user !=post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.body=form.body.data
        db.session.add(post)
        flash(u'动态已经更新！')
        return redirect(url_for('.post',id=post.id))
    form.body.data=post.body
    return render_template('edit_post.html',form=form)