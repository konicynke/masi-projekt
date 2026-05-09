from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.service.leave_service import create_leave_request, get_user_leaves, cancel_leave_request

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
        "status": leave.status.value
    } for leave in leaves]), 200

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