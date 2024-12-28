# -*- encoding: utf-8 -*-

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass
from datetime import datetime

class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    name = db.Column(db.String(64))  # Tên người dùng
    phone = db.Column(db.String(15), unique=True) 
    creation_time = db.Column(db.DateTime, default= datetime.now)  
    role_assignment_time = db.Column(db.DateTime)  
    last_login = db.Column(db.DateTime) 
    last_logout = db.Column(db.DateTime) 
    status = db.Column(db.Integer, default = 0)  # Trạng thái online của tài khoản


    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
