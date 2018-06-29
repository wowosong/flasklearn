# encoding=utf-8
from flask import  render_template,redirect,request,url_for,flash
from  flask_login import  login_user,logout_user,login_required,current_user
from . import  auth
import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
from ..email import send_email
from ..models import  User
from .forms import LoginForm,RegistrationForm,ChangePasswordForm,ResetRequestPasswordForm,ResetPasswordForm
from app import  db
@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'无效的用户名或密码！')
    return render_template('auth/login.html',form=form)
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'你已经登出！')
    return  redirect(url_for('main.index'))
@auth.route('/register',methods=['GET','POST'])
def register():
    form =RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token=user.generate_confirmation_token()
        send_email(user.email,u'确认账号','auth/email/confirm',user=user,token=token)
        flash(u'确认邮件已经发到您的邮箱！！！')
        return redirect(url_for('auth.login'))
        # return redirect('main.index')
    return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if  current_user.confirm(token):
        flash(u'现在可以登录了！！！')
    else:
        flash(u'确认链接无效或者过期！！！')
    return  redirect(url_for('main.index'))
@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5]!='auth.' and request.endpoint!='static':
        return  redirect(url_for('auth.unconfirmed'))
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return  redirect(url_for('main.index'))
    return render_template('/auth/unconfirmed.html')
@auth.route('/confirm')
@login_required
def send_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,u'确认账号','auth/email/confirm',user=current_user,token=token)
    flash(u'一封新的确认邮件已经发到您的邮箱，请查收！！！')
    return redirect(url_for('main.index'))
@auth.route('/resend_email')
# @login_required
def resend_email():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,u'确认账号','auth/email/confirm',user=current_user,token=token)
    flash(u'一封新的确认邮件已经发到您的邮箱，请查收！！！')
    return redirect(url_for('main.index'))
@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
    form=ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password=form.password.data
            db.session.add(current_user)
            flash(u'你的密码已经更新')
            return redirect(url_for('main.index'))
        else:
            flash(u'密码无效。', 'warning')
    return render_template("/auth/changepassword.html", form=form)
@auth.route('/reset_password',methods=['GET','POST'])
@login_required
def reset_password_request():
    if not current_user.is_anonymous:
        return  redirect(url_for('main.index'))
    form=ResetRequestPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email,u'重设密码', 'auth/email/reset_password',user=user,token=token,next=request.args.get('next'))
        flash(u'密码重设邮件已经发送到你的邮箱，请及时查收。', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/resetpassword.html',form=form)
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    print current_user.is_anonymous
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if current_user.reset_password(form.password.data):
        # if user.reset_password(form.password.data):
            flash(u'你的密码已经更新。', 'success')
            db.session.add(user)
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/resetpassword.html', form=form)

UPLOAD_FOLDER = '/path/to/the/uploads'

#上传文件代码
UPLOAD_FOLDER = 'D:\hjs'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
@auth.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('auth.upload_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''