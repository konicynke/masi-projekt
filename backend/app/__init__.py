import os
from flask import Flask
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager

from .extension import db, migrate, mail
from .controller.auth_controller import auth_bp
from .controller.leave_controller import leave_bp
from .controller.manager_controller import manager_bp
from .controller.admin_controller import admin_bp
from .controller.hr_controller import hr_bp

def create_app():
    app = Flask(__name__)

    load_dotenv()
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    with app.app_context():
        from .model.user import User
        from .model.department import Department
        from .model.leave_type import LeaveType
        from .model.leave_balance import LeaveBalance
        from .model.leave_request import LeaveRequest

    jwt = JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(leave_bp, url_prefix='/api/leaves')
    app.register_blueprint(manager_bp, url_prefix='/api/manager')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(hr_bp, url_prefix='/api/hr')

    return app