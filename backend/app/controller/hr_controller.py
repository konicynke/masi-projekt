from flask import Blueprint, jsonify, Response
from flask_jwt_extended import jwt_required
from app.service.hr_service import get_all_leaves, generate_leaves_csv_report
from app.utils.decorators import role_required

hr_bp = Blueprint('hr', __name__)

@hr_bp.route('/leaves', methods=['GET'])
@jwt_required()
@role_required('HR', 'ADMIN')
def list_all_leaves():
    leaves = get_all_leaves()
    return jsonify([{
        "id": leave.id,
        "user_id": leave.user_id,
        "leave_type_id": leave.leave_type_id,
        "start_date": leave.start_date.isoformat(),
        "end_date": leave.end_date.isoformat(),
        "status": leave.status.value,
        "reason": leave.request_reason
    } for leave in leaves]), 200

@hr_bp.route('/reports/csv', methods=['GET'])
@jwt_required()
@role_required('HR', 'ADMIN')
def export_leaves_csv():
    csv_data = generate_leaves_csv_report()
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=raport_urlopowy.csv"}
    )