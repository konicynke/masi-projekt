from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from app.extension import db
from app.model.user import User


def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        additional_claims = {"role": user.role.value}
        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
        return access_token, user
    return None, None


def get_user_profile(user_id: int) -> User:
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError("User not found.")
    return user


def update_user_profile(user_id: int, data: dict) -> User:
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError("User not found.")

    if 'first_name' in data and data['first_name']:
        user.first_name = data['first_name']
    if 'last_name' in data and data['last_name']:
        user.last_name = data['last_name']
    if 'email' in data and data['email']:
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ValueError("Email is already in use.")
        user.email = data['email']

    db.session.commit()
    return user
