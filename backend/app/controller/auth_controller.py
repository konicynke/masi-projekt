from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.service.auth_service import authenticate_user, get_user_profile, update_user_profile

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

    return jsonify({"msg": "Invalid email or password"}), 401


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = get_user_profile(int(user_id))
    return jsonify({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role.value,
    }), 200


@auth_bp.route('/me', methods=['PATCH'])
@jwt_required()
def edit_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    try:
        user = update_user_profile(int(user_id), data)
        return jsonify({
            "msg": "Profile updated successfully",
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
