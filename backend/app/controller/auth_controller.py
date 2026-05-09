from flask import Blueprint, request, jsonify
from app.service.auth_service import authenticate_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    token, user = authenticate_user(email, password)

    if token:
        return jsonify({
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "name": f"{user.first_name} {user.last_name}"
            }
        }), 200

    return jsonify({
        "msg": "Invalid email or password"
    }), 401