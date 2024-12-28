# -*- encoding: utf-8 -*-

from apps import db
from flask_socketio import emit
from datetime import datetime
from apps.authentication.models import Users

###################   PHÂN QUYỀN   ##############################

class Role(db.Model):
    __tablename__ = 'Role'

    id = db.Column(db.Integer ,primary_key = True)
    name = db.Column(db.String(64))
    def __init__(self , name ):
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

class Project_list(db.Model):
    __tablename__ = 'Project_list'

    id = db.Column(db.Integer ,primary_key = True)
    name = db.Column(db.String(64))
    address = db.Column(db.String(64))
    type = db.Column(db.String(64))
    investor = db.Column(db.String(64))
    def __init__(self , name, address, type, investor ):
        self.name = name
        self.address = address
        self.type = type
        self.investor = investor

    def save(self):
        db.session.add(self)
        db.session.commit()

# Map 3 bảng trên lại với nhau
class User_project_role(db.Model):
    __tablename__ = 'User_project_role'

    id = db.Column(db.Integer ,primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id") ,nullable = False)
    project_id = db.Column(db.Integer, db.ForeignKey("Project_list.id") ,nullable = False)
    role_id = db.Column(db.Integer, db.ForeignKey("Role.id") ,nullable = False)

    def __init__(self , user_id, project_id, role_id ):
        self.user_id = user_id
        self.project_id = project_id
        self.role_id = role_id

    def save(self):
        db.session.add(self)
        db.session.commit()

class Page(db.Model):
    __tablename__ = 'Page'

    id = db.Column(db.Integer ,primary_key = True)
    url = db.Column(db.String(64))
    description = db.Column(db.String(64))   
    def __init__(self , url, description ):
        self.url = url
        self.description = description

    def save(self):
        db.session.add(self)
        db.session.commit()

class Method_list(db.Model):
    __tablename__ = 'Method_list'

    id = db.Column(db.Integer ,primary_key = True)
    method = db.Column(db.String(64))
    def __init__(self , method):
        self.method = method

    def save(self):
        db.session.add(self)
        db.session.commit()

class Permissions(db.Model):
    __tablename__ = 'Permissions'

    id = db.Column(db.Integer ,primary_key = True)
    page_id = db.Column(db.Integer, db.ForeignKey("Page.id") ,nullable = False)
    method_id = db.Column(db.Integer, db.ForeignKey("Method_list.id") ,nullable = False)
    description = db.Column(db.String(64))   

    def __init__(self , page_id, method_id, description ):
        self.page_id = page_id
        self.method_id = method_id
        self.description = description

    def save(self):
        db.session.add(self)
        db.session.commit()

#Map bảng role với permission
class Role_permissions(db.Model):
    __tablename__ = 'Role_permissions'

    id = db.Column(db.Integer ,primary_key = True)
    role_id = db.Column(db.Integer, db.ForeignKey("Role.id") ,nullable = False)
    permission_id = db.Column(db.Integer, db.ForeignKey("Permissions.id") ,nullable = False) 

    def __init__(self , role_id, permission_id ):
        self.role_id = role_id
        self.permission_id = permission_id

    def save(self):
        db.session.add(self)
        db.session.commit()

#############################   Thông tin bán hàng  #################################

class Project_1(db.Model):
    __tablename__ = 'Project_1'

    id = db.Column(db.Integer, primary_key=True)
    floor_id = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, nullable=False)
    areas = db.Column(db.Integer, nullable=False)
    acreage = db.Column(db.String(50), nullable=False)  
    bedroom = db.Column(db.Integer, nullable=False)
    bathroom = db.Column(db.Integer, nullable=False)
    direction = db.Column(db.Integer, nullable=True) 
    status = db.Column(db.Integer, default=0)  
    price = db.Column(db.String(50), nullable=False) 
    utility = db.Column(db.String(100), nullable=True)
    power = db.Column(db.Integer, default=0)  

    def __init__(self, floor_id, room_id, areas, acreage, bedroom, bathroom, direction, status, price, utility, power):
        self.floor_id = floor_id
        self.room_id = room_id
        self.areas = areas
        self.acreage = acreage
        self.bedroom = bedroom
        self.bathroom = bathroom
        self.direction = direction
        self.status = status
        self.price = price
        self.utility = utility
        self.power = power
    def save(self):
        db.session.add(self)
        db.session.commit()