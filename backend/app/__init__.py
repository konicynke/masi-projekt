import os
from flask import Flask
from dotenv import load_dotenv
from .extension import db, migrate

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

    return app