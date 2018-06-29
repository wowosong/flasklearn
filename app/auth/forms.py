# encoding=utf-8
from  flask_wtf import  FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User
class LoginForm(FlaskForm):
    email=StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
    password=PasswordField(u'密码',validators=[Required()])
    remember_me=BooleanField(u'保持登录')
    sumbit=SubmitField(u'登录')
class RegistrationForm(FlaskForm):
    email=StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
    username=StringField(u'用户名',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,u'用户名只能包括字母、数字、下划线')])
    password=PasswordField(u'密码',validators=[Required(),EqualTo('password2',message=u'确认密码必须与密码一致')])
    password2=PasswordField(u'确认密码',validators=[Required()])
    sumbit=SubmitField(u'注册')
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise  ValidationError(u'邮箱已经注册！')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise  ValidationError(u'用户名已经使用过！.')
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField( u'旧密码',validators=[Required(message=u'密码不能为空')])
    password = PasswordField(u'新密码',validators=[Required(message=u'密码不能为空'),EqualTo('password2',message=u'密码必须匹配')])
    password2 = PasswordField(u'确认密码',validators=[Required()])
    sumbit = SubmitField(u'提交密码')

    def validate_password(self, field):
        if User.query.filter_by(password=field.data).first():
            raise ValidationError(u'密码不能与原密码一致！')
class ResetRequestPasswordForm(FlaskForm):
    email = StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
    sumbit = SubmitField(u'重置')
class ResetPasswordForm(FlaskForm):
    email = StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
    username = StringField(u'用户名',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,u'用户名只能包括字母、数字、下划线')])
    password = PasswordField(u'密码',validators=[Required(),EqualTo('password2',message=u'密码必须与确认密码一致')])
    # password = PasswordField('Password',validators=[Required()])
    password2 = PasswordField(u'确认密码',validators=[Required()])
    sumbit = SubmitField(u'重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(u'邮箱地址有错，请检查。')

class ChangeEmailForm(FlaskForm):
    email = StringField(u'新邮箱地址', validators=[Required(message= u'邮箱不能为空'), Length(1, 64),
                                                 Email(message= u'请输入有效的邮箱地址，比如：username@domain.com')])
    password = PasswordField(u'密码', validators=[Required(message= u'密码不能为空')])
    submit = SubmitField(u'更新')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已经注册过了，换一个吧。')