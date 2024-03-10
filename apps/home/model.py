# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from apps import db
from flask_socketio import emit
from sqlalchemy import DateTime
from datetime import datetime

class Room(db.Model):
    __tablename__ = 'Room'

    id = db.Column(db.Integer ,primary_key = True)
    name = db.Column(db.String(64), nullable = False)
    description = db.Column(db.String(64))

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, key, value)

    # def __init__(self ,name ,description):
    #     self.name = name
    #     self.description = description

    def save(self):
        db.session.add(self)
        db.session.commit()

class Device(db.Model):
    __tablename__ = 'Device'

    id = db.Column(db.String(64) ,primary_key = True)
    room_id = db.Column(db.Integer, db.ForeignKey("Room.id") ,nullable = False)
    name = db.Column(db.String(64), nullable = False)
    type = db.Column(db.String(64), nullable = False)
    description = db.Column(db.String(64))
    create_time = db.Column(db.DateTime ,default = datetime.now)
    update_time = db.Column(db.DateTime ,default = datetime.now)
    info = db.Column(db.String(64))

    def __init__(self , id ,room_id ,name ,type ,description ,create_time ,update_time ,info ):
        self.id = id
        self.room_id = room_id
        self.name = name
        self.type = type
        self.description = description
        self.create_time = create_time
        self.update_time = update_time
        self.info = info

    def save(self):
        db.session.add(self)
        db.session.commit()

class DeviceState(db.Model):
    __tablename__ = 'DeviceState'

    id = db.Column(db.Integer ,primary_key = True)
    device_id = db.Column(db.String(64), db.ForeignKey("Device.id") ,nullable = False)
    print(datetime.utcnow())
    time_stamp = db.Column(db.DateTime ,default = datetime.now)
    resource = db.Column(db.String(64))
    value = db.Column(db.String(64))

    def __init__(self , device_id ,time_stamp ,resource ,value ):
        self.device_id = device_id
        self.time_stamp = time_stamp
        self.resource = resource
        self.value = value

    def save(self):
        db.session.add(self)
        db.session.commit()

class RoomStatus(db.Model):
    __tablename__ = 'RoomStatus'

    id = db.Column(db.Integer ,primary_key = True)
    room_id = db.Column(db.String(64), db.ForeignKey("Room.id") ,nullable = False)
    time_stamp = db.Column(db.DateTime ,default = datetime.now)
    resource = db.Column(db.String(64))
    value = db.Column(db.String(64))
    time_condition = db.Column(db.Integer)


    def __init__(self , room_id ,time_stamp ,resource ,value , time_condition ):
        self.room_id = room_id
        self.time_stamp = time_stamp
        self.resource = resource
        self.value = value
        self.time_condition = time_condition

    def save(self):
        db.session.add(self)
        db.session.commit()

class RuleCondition(db.Model):
    __tablename__ = 'RuleCondition'

    id = db.Column(db.Integer ,primary_key = True ,autoincrement=True )
    resource = db.Column(db.String(64))
    condition = db.Column(db.String(64))
    value = db.Column(db.String(64))

    def __init__(self  ,resource ,condition ,value ):
        self.resource = resource
        self.condition = condition
        self.value = value

    def save(self):
        db.session.add(self)
        db.session.commit()

class RuleAction(db.Model):
    __tablename__ = 'RuleAction'

    id = db.Column(db.Integer ,primary_key = True ,autoincrement=True)
    id_rule = db.Column(db.String(64), db.ForeignKey("RuleCondition.id") ,nullable = False)
    device = db.Column(db.String(64))
    value = db.Column(db.String(64))

    def __init__(self , id_rule , device ,value ):
        self.id_rule = id_rule
        self.device = device
        self.value = value

    def save(self):
        db.session.add(self)
        db.session.commit()     

class Sales(db.Model):
    __tablename__ = 'Sales'
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(64))
    amount = db.Column(db.String(64))
    status = db.Column(db.Enum('Completed', 'Not Completed'), default='Not Completed')

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            setattr(self, key, value)
    def __repr__(self):
        return str(self.product)
    def save(self):
        db.session.add(self)
        db.session.commit()
