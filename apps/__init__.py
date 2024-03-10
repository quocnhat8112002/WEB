# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os

from flask import Flask ,current_app
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module

from apps.events import socketio, events_init
from apscheduler.schedulers.background import BackgroundScheduler


db = SQLAlchemy()
login_manager = LoginManager()


def register_extensions(app):
    from apps.home.model import Sales

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

    #gọi hàm thực hiện lịch
    # register_scheduler_job(app)

# Thêm hàm đăng ký công việc lên lịch
def register_scheduler_job(app):
    from .rule import scheduler ,check_conditions
    # Đăng ký công việc kiểm tra mỗi 1 phút
    scheduler.add_job(check_conditions, 'interval', minutes=0.2)
    # seconds=0.1
    # Bắt đầu lịch
    scheduler.start()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    socketio.init_app(app)
    events_init('broker.emqx.io' )
    return app
