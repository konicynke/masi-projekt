from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.service.admin_service import (
    create_new_user,
    create_new_leave_type,
    create_new_balance,
    create_new_department,
    assign_user_to_department,
)
from app.model.user import User, UserRole
from app.model.leave_type import LeaveType
from app.model.department import Department
from app.extension import db
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
            manager_id=data.get('manager_id'),
            department_id=data.get('department_id'),
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


@admin_bp.route('/departments', methods=['POST'])
@jwt_required()
@role_required('ADMIN')
def add_department():
    data = request.get_json()
    try:
        dept = create_new_department(name=data['name'])
        return jsonify({"msg": "Department created", "id": dept.id}), 201
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    except KeyError as e:
        return jsonify({"msg": f"Missing required field: {str(e)}"}), 400


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def list_users():
    dept_map = {d.id: d.name for d in Department.query.all()}
    users = User.query.order_by(User.last_name).all()
    return jsonify([{
        "id": u.id,
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "role": u.role.value,
        "manager_id": u.manager_id,
        "department_id": u.department_id,
        "department_name": dept_map.get(u.department_id),
    } for u in users]), 200


@admin_bp.route('/departments', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def list_departments():
    depts = Department.query.all()
    return jsonify([{"id": d.id, "name": d.name} for d in depts]), 200


@admin_bp.route('/leave-types', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def list_leave_types():
    types = LeaveType.query.all()
    return jsonify([{
        "id": t.id,
        "name": t.name,
        "requires_approval": t.requires_approval,
    } for t in types]), 200


@admin_bp.route('/users/<int:user_id>', methods=['PATCH'])
@jwt_required()
@role_required('ADMIN')
def edit_user(user_id):
    data = request.get_json()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    try:
        if 'role' in data and data['role']:
            user.role = UserRole(data['role'].upper())
        if 'manager_id' in data:
            user.manager_id = data['manager_id']
        if 'department_id' in data:
            user.department_id = data['department_id']
        db.session.commit()
        return jsonify({"msg": "User updated", "id": user.id}), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400


@admin_bp.route('/users/<int:user_id>/department', methods=['PATCH'])
@jwt_required()
@role_required('ADMIN')
def assign_department(user_id):
    data = request.get_json()
    try:
        user = assign_user_to_department(user_id, data.get('department_id'))
        return jsonify({
            "msg": "Department assigned",
            "user_id": user.id,
            "department_id": user.department_id
        }), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
