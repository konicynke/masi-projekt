from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.service.admin_service import create_new_user, create_new_leave_type, create_new_balance
from app.model.user import UserRole
from app.utils.decorators import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
@role_required('ADMIN')
def add_user():
    data = request.get_json()
    try:
        role_enum = UserRole(data.get('role', 'EMPLOYEE').upper())
        user = create_new_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role_enum,
            manager_id=data.get('manager_id')
        )
        return jsonify({"msg": "User created", "id": user.id}), 201
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except KeyError as e:
        return jsonify({"msg": f"Missing required field: {str(e)}"}), 400

@admin_bp.route('/leave-types', methods=['POST'])
@jwt_required()
@role_required('ADMIN')
def add_leave_type():
    data = request.get_json()
    try:
        leave_type = create_new_leave_type(
            name=data['name'],
            requires_approval=data.get('requires_approval', True)
        )
        return jsonify({"msg": "Leave type created", "id": leave_type.id}), 201
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except KeyError as e:
        return jsonify({"msg": f"Missing required field: {str(e)}"}), 400

@admin_bp.route('/balances', methods=['POST'])
@jwt_required()
@role_required('ADMIN')
def add_balance():
    data = request.get_json()
    try:
        balance = create_new_balance(
            user_id=data['user_id'],
            leave_type_id=data['leave_type_id'],
            year=data['year'],
            total_days=data['total_days']
        )
        return jsonify({"msg": "Balance created", "id": balance.id}), 201
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except KeyError as e:
        return jsonify({"msg": f"Missing required field: {str(e)}"}), 400