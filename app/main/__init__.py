#encoding=utf-8
from flask import  Blueprint
from app.models import Permission
main=Blueprint('main',__name__)
from .import views,errors
#防止循环导入依赖
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)