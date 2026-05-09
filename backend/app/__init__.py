import os
from flask import Flask
from dotenv import load_dotenv
from .extension import db, migrate
from flask_jwt_extended import JWTManager
from .controller.auth_controller import auth_bp
from .controller.leave_controller import leave_bp
from .controller.manager_controller import manager_bp

def create_app():
    app = Flask(__name__)

    load_dotenv()
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from .model.user import User
        from .model.leave_type import LeaveType
        from .model.leave_balance import LeaveBalance
        from .model.leave_request import LeaveRequest

    jwt = JWTManager(app)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(leave_bp, url_prefix='/api/leaves')
    app.register_blueprint(manager_bp, url_prefix='/api/manager')

    return app