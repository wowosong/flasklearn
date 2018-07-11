# encoding=utf-8
from wtforms import StringField,SubmitField,TextAreaField,BooleanField,SelectField
from wtforms.validators import Required,Length,Email,Regexp,ValidationError
from  flask_wtf import FlaskForm
from app.models import Role,User
from flask_pagedown.fields import PageDownField
class NameForm(FlaskForm):
    name=StringField(u'你的名字？',validators=[Required()])
    submit=SubmitField(u'提交')
class EditProfileForm(FlaskForm):
    name=StringField(u'真名',validators=[Length(0.64)])
    location=StringField(u'位置',validators=[Length(0,64)])
    about_me=TextAreaField(u'简介')
    submit=SubmitField(u'保存')
class EditProfileAdminForm(FlaskForm):
    email=StringField(u'邮箱',validators=[Required(),Length(1.64),Email()])
    username=StringField(u'用户名',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,u'用户名只能由字母、数字、下划线租成!!!')])
    confirmed=BooleanField(u'确认')
    role=SelectField(u'角色',coerce=int)
    name=StringField(u'真名',validators=[Length(0.64)])
    location=StringField(u'位置',validators=[Length(0,64)])
    about_me=TextAreaField(u'简介')
    submit=SubmitField(u'保存')
    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices=[(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
        self.user=user
    def validate_email(self,field):
        if field.data!=self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已经注册!!!')
    def validate_username(self,field):
        if field.data!=self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经使用!!!')
class PostForm(FlaskForm):
    # body=TextAreaField(u'请发布',validators=[Required()])
    body=PageDownField(u'请发布',validators=[Required()])
    submit=SubmitField(u'发布')
class CommentForm(FlaskForm):
    body=StringField('',validators=[Required()])
    submit=SubmitField('Submit')
