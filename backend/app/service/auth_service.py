from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token
from app.model.user import User

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        additional_claims = {"role": user.role.value}
        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
        return access_token, user
    
    return None, None