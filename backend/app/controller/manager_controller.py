from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.service.leave_service import get_team_leaves, update_leave_status
from app.model.leave_request import LeaveRequestStatus
from app.utils.decorators import role_required

manager_bp = Blueprint('manager', __name__)


@manager_bp.route('/team-leaves', methods=['GET'])
@jwt_required()
@role_required('MANAGER')
def list_team_leaves():
    current_manager_id = get_jwt_identity()
    leaves = get_team_leaves(int(current_manager_id))
    return jsonify(leaves), 200


@manager_bp.route('/leaves/<int:request_id>/status', methods=['PATCH'])
@jwt_required()
@role_required('MANAGER')
def change_leave_status(request_id):
    current_manager_id = get_jwt_identity()
    data = request.get_json()

    try:
        new_status_str = data.get('status')

        if not new_status_str:
            return jsonify({"msg": "Status is required."}), 400

        try:
            new_status_enum = LeaveRequestStatus(new_status_str.upper())
        except ValueError:
            return jsonify({
                "msg": "Invalid status value. Must be APPROVED or REJECTED."
            }), 400

        comment = data.get('comment')

        if new_status_enum == LeaveRequestStatus.REJECTED and not comment:
            return jsonify({"msg": "Uzasadnienie jest wymagane przy odrzuceniu wniosku."}), 400

        updated_req = update_leave_status(
            request_id=request_id,
            manager_id=int(current_manager_id),
            new_status=new_status_enum,
            comment=comment
        )

        return jsonify({
            "msg": "Leave status updated successfully",
            "id": updated_req.id,
            "new_status": updated_req.status.value
        }), 200

    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
