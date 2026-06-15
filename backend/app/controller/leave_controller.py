from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.service.leave_service import (
    create_leave_request,
    get_user_leaves,
    cancel_leave_request,
    get_user_balance,
    edit_leave_request,
)
from app.model.leave_type import LeaveType

leave_bp = Blueprint('leaves', __name__)


@leave_bp.route('', methods=['POST'])
@jwt_required()
def add_leave():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        new_req = create_leave_request(
            user_id=int(current_user_id),
            leave_type_id=data['leave_type_id'],
            start_date=start_date,
            end_date=end_date,
            reason=data.get('reason')
        )

        return jsonify({
            "msg": "Leave request submitted",
            "id": new_req.id
        }), 201

    except ValueError as e:
        return jsonify({"msg": str(e)}), 400


@leave_bp.route('/my', methods=['GET'])
@jwt_required()
def list_my_leaves():
    current_user_id = get_jwt_identity()
    leaves = get_user_leaves(int(current_user_id))

    return jsonify([{
        "id": leave.id,
        "start": leave.start_date.isoformat(),
        "end": leave.end_date.isoformat(),
        "status": leave.status.value,
        "leave_type_id": leave.leave_type_id,
        "reason": leave.request_reason,
    } for leave in leaves]), 200


@leave_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_balance():
    current_user_id = get_jwt_identity()
    balances = get_user_balance(int(current_user_id))
    return jsonify(balances), 200


@leave_bp.route('/types', methods=['GET'])
@jwt_required()
def get_leave_types():
    types = LeaveType.query.all()
    return jsonify([{"id": t.id, "name": t.name} for t in types]), 200


@leave_bp.route('/<int:request_id>', methods=['PATCH'])
@jwt_required()
def edit_leave(request_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()

    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        updated = edit_leave_request(
            request_id=request_id,
            user_id=int(current_user_id),
            start_date=start_date,
            end_date=end_date,
            leave_type_id=data['leave_type_id'],
            reason=data.get('reason'),
        )

        return jsonify({"msg": "Leave request updated", "id": updated.id}), 200

    except ValueError as e:
        return jsonify({"msg": str(e)}), 400


@leave_bp.route('/<int:request_id>/cancel', methods=['PATCH'])
@jwt_required()
def cancel_leave(request_id):
    current_user_id = get_jwt_identity()

    try:
        cancelled_req = cancel_leave_request(request_id, int(current_user_id))
        return jsonify({
            "msg": "Leave request cancelled successfully",
            "status": cancelled_req.status.value
        }), 200
    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
